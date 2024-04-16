use std::env;

pub mod ecc;

fn main() {

    let iter = 100;

    let args: Vec<String> = env::args().collect();

    if args[1] == String::from("ecc_secp256k1_sha256") {
        ecc::test::ecc_secp256k1_sha256(iter.clone());
    }

}
