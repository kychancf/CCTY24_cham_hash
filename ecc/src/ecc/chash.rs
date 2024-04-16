use std::time::Instant;

use curv::BigInt;
use curv::arithmetic::Samplable;
use curv::arithmetic::Modulo;
use curv::arithmetic::Converter;

use serde::{Deserialize, Serialize};

use curv::elliptic::curves::ECScalar;
use curv::elliptic::curves::ECPoint;

use curv::elliptic::curves::secp256_k1::Secp256k1Scalar;
use curv::elliptic::curves::secp256_k1::Secp256k1Point;

use sha2::Digest;
use sha2::Sha256;

#[derive(Clone, Debug)]
pub struct CHASH<S: ECScalar, P: ECPoint> {
    pub h: P,
    pub r: (S, S, S)
}

impl CHASH<Secp256k1Scalar, Secp256k1Point> {

    pub fn chash_secp256k1_sha256 (
        q: BigInt,  
        pk: Secp256k1Point, 
        m: BigInt,
    ) -> (Self, u128) {

        // Prepare hasher
        let mut hasher: Sha256 = Sha256::new();
        let mut hasher_c1: Sha256 = Sha256::new();
        let mut hasher_c2: Sha256 = Sha256::new();

        let start = Instant::now();

        // Sample random rho
        let rho: BigInt = BigInt::sample_below(&q);
        let rho_fe: Secp256k1Scalar = ECScalar::from_bigint(&rho);

        // Calculate h
        hasher.update(m.to_bytes()); // m in hex
        let result: BigInt = BigInt::from_bytes(&hasher.finalize());
        let result_fe: Secp256k1Scalar = ECScalar::from_bigint(&result);
        let g_rho: Secp256k1Point = ECPoint::generator_mul(&rho_fe);
        let h: Secp256k1Point = g_rho.scalar_mul(&result_fe);
        // println!("g_rho: {:?}", g_rho);
        // println!("h: {:?}", h);

        // The NIZK proof
        // ========== Step (1) ==========
        let t2: BigInt = BigInt::sample_below(&q);
        let t2_fe: Secp256k1Scalar = ECScalar::from_bigint(&t2);
        let z1: BigInt = BigInt::sample_below(&q);
        let z1_fe: Secp256k1Scalar = ECScalar::from_bigint(&z1);
        // println!("t2_fe: {:?}", t2_fe);
        // println!("z1_fe: {:?}", z1_fe);

        // T2
        let T2: Secp256k1Point = ECPoint::generator_mul(&t2_fe);
        // println!("T2: {:?}", T2);

        // c1
        let mut message_c1: Vec<u8> = BigInt::from_bytes(&T2.serialize_compressed()).to_bytes();
        message_c1.extend(&BigInt::from_bytes(&pk.serialize_compressed()).to_bytes());
        message_c1.extend(&BigInt::from_bytes(&g_rho.serialize_compressed()).to_bytes());
        message_c1.extend(&m.modulus(&q).to_bytes());
        hasher_c1.update(&message_c1);
        let c1: BigInt = BigInt::from_bytes(&hasher_c1.finalize());
        let c1_fe: Secp256k1Scalar = ECScalar::from_bigint(&c1);
        // println!("c1: {:?}", c1);

        // T1
        let g_z1: Secp256k1Point = ECPoint::generator_mul(&z1_fe);
        let pk_c1: Secp256k1Point = pk.scalar_mul(&ECScalar::from_bigint(&c1));
        let T1: Secp256k1Point = g_z1.add_point(&pk_c1);
        // println!("T1: {:?}", T1);

        // The NIZK proof
        // ========== Step (2) ==========
        let mut message_c2: Vec<u8> = BigInt::from_bytes(&T1.serialize_compressed()).to_bytes();
        message_c2.extend(&BigInt::from_bytes(&pk.serialize_compressed()).to_bytes());
        message_c2.extend(&BigInt::from_bytes(&g_rho.serialize_compressed()).to_bytes());
        message_c2.extend(&m.modulus(&q).to_bytes());
        hasher_c2.update(&message_c2);
        let c2: BigInt = BigInt::from_bytes(&hasher_c2.finalize());
        // println!("c2: {:?}", c2);

        // The NIZK proof
        // ========== Step (3) ==========
        let c2rho: BigInt = BigInt::mod_mul(&c2, &rho, &q);
        let minus_c2rho: BigInt = BigInt::mod_mul(&c2rho, &BigInt::from(-1), &q);
        let z2: BigInt = BigInt::mod_add(&t2, &minus_c2rho, &q);
        let z2_fe: Secp256k1Scalar = ECScalar::from_bigint(&z2);
        // println!("z2: {:?}", z2);

        let time = start.elapsed().as_nanos(); 

        (
            CHASH {
                h: h,
                r: (z1_fe, z2_fe, c1_fe)
            },
            time
        )
    }

}