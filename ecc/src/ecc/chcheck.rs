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

pub fn chcheck_secp256k1_sha256 (
    q: BigInt, 
    pk: Secp256k1Point,
    m: BigInt,
    h: Secp256k1Point,
    r: (Secp256k1Scalar, Secp256k1Scalar, Secp256k1Scalar)
) -> (bool, u128) {

    // Prepare hasher
    let mut hasher: Sha256 = Sha256::new();
    let mut hasher_c1_test: Sha256 = Sha256::new();
    let mut hasher_c2: Sha256 = Sha256::new();

    let start = Instant::now();

    // Parse r
    let (z1_fe, z2_fe, c1_fe) = r;
    // println!("z1_fe: {:?}", z1_fe);
    // println!("z2_fe: {:?}", z2_fe);
    // println!("c1_fe: {:?}", c1_fe);

    // Calculate y'
    hasher.update(m.to_bytes()); // m in hex
    let result: BigInt = BigInt::from_bytes(&hasher.finalize()); // H(m)
    let result_fe: Secp256k1Scalar = ECScalar::from_bigint(&result);
    let result_inv: Secp256k1Scalar = result_fe.invert().unwrap();
    let y_prime: Secp256k1Point = h.scalar_mul(&result_inv);;
    // println!("y_prime: {:?}", y_prime);
    // println!("result_inv: {:?}", result_inv);

    // ========== Check conditions ==========
    // T1
    let g_z1: Secp256k1Point = ECPoint::generator_mul(&z1_fe);
    let pk_c1: Secp256k1Point = pk.scalar_mul(&c1_fe);
    let T1: Secp256k1Point = g_z1.add_point(&pk_c1);

    // c2
    let mut message_c2: Vec<u8> = BigInt::from_bytes(&T1.serialize_compressed()).to_bytes();
    message_c2.extend(&BigInt::from_bytes(&pk.serialize_compressed()).to_bytes());
    message_c2.extend(&BigInt::from_bytes(&y_prime.serialize_compressed()).to_bytes());
    message_c2.extend(&m.modulus(&q).to_bytes());
    hasher_c2.update(&message_c2);
    let c2: BigInt = BigInt::from_bytes(&hasher_c2.finalize());
    let c2_fe: Secp256k1Scalar = ECScalar::from_bigint(&c2);
    // println!("c2: {:?}", c2);

    // T2
    let g_z2: Secp256k1Point = ECPoint::generator_mul(&z2_fe);
    let y_prime_c2: Secp256k1Point = y_prime.scalar_mul(&c2_fe);
    let T2: Secp256k1Point = g_z2.add_point(&y_prime_c2);
    // println!("g_z2: {:?}", g_z2);
    // println!("y_prime_c2: {:?}", y_prime_c2);
    // println!("T2: {:?}", T2);

    // c1 test
    let mut message_c1_test: Vec<u8> = BigInt::from_bytes(&T2.serialize_compressed()).to_bytes();
    message_c1_test.extend(&BigInt::from_bytes(&pk.serialize_compressed()).to_bytes());
    message_c1_test.extend(&BigInt::from_bytes(&y_prime.serialize_compressed()).to_bytes());
    message_c1_test.extend(&m.modulus(&q).to_bytes());
    hasher_c1_test.update(&message_c1_test);
    let c1_test: BigInt = BigInt::from_bytes(&hasher_c1_test.finalize());
    let c1_test_fe: Secp256k1Scalar = ECScalar::from_bigint(&c1_test);
    // println!("c1: {:?}", c1_fe);

    let time = start.elapsed().as_nanos(); 

    (
        c1_fe == c1_test_fe,
        time
    )
}