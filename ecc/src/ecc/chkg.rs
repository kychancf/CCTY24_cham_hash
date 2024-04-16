use std::time::Instant;

use curv::BigInt;
use curv::arithmetic::Samplable;
use curv::arithmetic::Modulo;

use serde::{Deserialize, Serialize};

use curv::elliptic::curves::ECScalar;
use curv::elliptic::curves::ECPoint;

use curv::elliptic::curves::secp256_k1::Secp256k1Scalar;
use curv::elliptic::curves::secp256_k1::Secp256k1Point;

#[derive(Clone, Debug, PartialEq)]
pub struct CHKG<S: ECScalar, P: ECPoint> {
    pub pk: P,
    pub sk: S 
}

impl CHKG<Secp256k1Scalar, Secp256k1Point> {
    
    pub fn chkg_secp256k1 (
        q: BigInt
    ) -> (Self, u128) {

        let start = Instant::now();

        let x: Secp256k1Scalar = ECScalar::from_bigint(&BigInt::sample_below(&q));
        // let pk: BigInt = BigInt::mod_pow(&g, &x, &p);
        let pk: Secp256k1Point = ECPoint::generator_mul(&x);

        let time = start.elapsed().as_nanos(); 

        (
            Self {
                pk: pk,
                sk: x
            },
            time
        )
    }
}
