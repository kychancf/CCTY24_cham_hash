use std::process;

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

use std::time::Instant;

#[derive(Clone, Debug)]
pub struct CHADAPT<S: ECScalar> {
    pub r_prime: (S, S, S)
}

impl CHADAPT<Secp256k1Scalar> {

    pub fn chadapt_secp256k1_sha256 (
        q: BigInt,  
        pk: Secp256k1Point, 
        sk: Secp256k1Scalar, 
        m: BigInt,
        m_prime: BigInt,
        h: Secp256k1Point,
        r: (Secp256k1Scalar, Secp256k1Scalar, Secp256k1Scalar)
    ) -> (Self, u128, u128) {

        let (chcheck_result, chcheck_time) = super::chcheck::chcheck_secp256k1_sha256(
            q.clone(), 
            pk.clone(), 
            m.clone(), 
            h.clone(), 
            r.clone()
        );

        if chcheck_result == false {
            println!("chcheck failed... Terminating...");
            process::exit(1)
        }
        else {
            // println!("chcheck passed!");
        }

        // Prepare hasher
        let mut hasher: Sha256 = Sha256::new();
        let mut hasher_c1_prime: Sha256 = Sha256::new();
        let mut hasher_c2_prime: Sha256 = Sha256::new();

        let start = Instant::now();

        // Calculate y'
        hasher.update(m_prime.to_bytes()); // m in hex
        let result: BigInt = BigInt::from_bytes(&hasher.finalize()); // H(m)
        let result_fe: Secp256k1Scalar = ECScalar::from_bigint(&result);
        let result_inv: Secp256k1Scalar = result_fe.invert().unwrap();
        let y_prime: Secp256k1Point = h.scalar_mul(&result_inv);;
        // println!("y_prime: {:?}", y_prime);
        // println!("result_inv: {:?}", result_inv);

        // The NIZK proof for r'
        // ========== Step (1) ==========
        let t1_prime: BigInt = BigInt::sample_below(&q);
        let t1_prime_fe: Secp256k1Scalar = ECScalar::from_bigint(&t1_prime);
        let z2_prime: BigInt = BigInt::sample_below(&q);
        let z2_prime_fe: Secp256k1Scalar = ECScalar::from_bigint(&z2_prime);
        // println!("t1_prime_fe: {:?}", t1_prime_fe);
        // println!("z2_prime_fe: {:?}", z2_prime_fe);

        // T1_prime
        let T1_prime: Secp256k1Point = ECPoint::generator_mul(&t1_prime_fe);
        // println!("T1_prime: {:?}", T1_prime);

        // c2_prime
        let mut message_c2_prime: Vec<u8> = BigInt::from_bytes(&T1_prime.serialize_compressed()).to_bytes();
        message_c2_prime.extend(&BigInt::from_bytes(&pk.serialize_compressed()).to_bytes());
        message_c2_prime.extend(&BigInt::from_bytes(&y_prime.serialize_compressed()).to_bytes());
        message_c2_prime.extend(&m_prime.modulus(&q).to_bytes());
        hasher_c2_prime.update(&message_c2_prime);
        let c2_prime: BigInt = BigInt::from_bytes(&hasher_c2_prime.finalize());
        let c2_prime_fe: Secp256k1Scalar = ECScalar::from_bigint(&c2_prime);
        // println!("c2_prime: {:?}", c2_prime);

        // T2_prime
        let g_z2_prime: Secp256k1Point = ECPoint::generator_mul(&z2_prime_fe);
        let y_prime_c2_prime: Secp256k1Point = y_prime.scalar_mul(&c2_prime_fe);
        let T2_prime: Secp256k1Point = g_z2_prime.add_point(&y_prime_c2_prime);

        // ========== Step (2) ==========
        // c1_prime
        let mut message_c1_prime: Vec<u8> = BigInt::from_bytes(&T2_prime.serialize_compressed()).to_bytes();
        message_c1_prime.extend(&BigInt::from_bytes(&pk.serialize_compressed()).to_bytes());
        message_c1_prime.extend(&BigInt::from_bytes(&y_prime.serialize_compressed()).to_bytes());
        message_c1_prime.extend(&m_prime.modulus(&q).to_bytes());
        hasher_c1_prime.update(&message_c1_prime);
        let c1_prime: BigInt = BigInt::from_bytes(&hasher_c1_prime.finalize());
        let c1_prime_fe: Secp256k1Scalar = ECScalar::from_bigint(&c1_prime);
        // println!("c1_prime: {:?}", c1_prime);

        // ========== Step (3) ==========
        let c1_prime_x: BigInt = BigInt::mod_mul(&c1_prime, &sk.to_bigint(), &q);
        let minus_c1_prime_x: BigInt = BigInt::mod_mul(&c1_prime_x, &BigInt::from(-1), &q);
        let z1_prime: BigInt = BigInt::mod_add(&t1_prime, &minus_c1_prime_x, &q);
        let z1_prime_fe: Secp256k1Scalar = ECScalar::from_bigint(&z1_prime);
        // println!("z1_prime: {:?}", z1_prime);

        let chadapt_time = start.elapsed().as_nanos(); 

        (
            CHADAPT {
                r_prime: (z1_prime_fe, z2_prime_fe, c1_prime_fe)
            },
            chcheck_time,
            chadapt_time
        )
    }
}