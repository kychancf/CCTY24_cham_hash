use curv::BigInt;
use curv::arithmetic::Converter;

use curv::elliptic::curves::ECScalar;
use curv::elliptic::curves::ECPoint;

use curv::elliptic::curves::secp256_k1::Secp256k1Scalar;
use curv::elliptic::curves::secp256_k1::Secp256k1Point;

use curv::elliptic::curves::p256::Secp256r1Scalar;
use curv::elliptic::curves::p256::Secp256r1Point;

pub fn get_secp256k1_info() -> (BigInt, Secp256k1Point) {

    // The group order p
    // 115792089237316195423570985008687907852837564279074904382605163141518161494337
    let q: &BigInt = Secp256k1Scalar::group_order();
    // println!("order: {:?}", q);

    // // The prime
    // // 115792089237316195423570985008687907853269984665640564039457584007908834671663
    // // 1852673427797059126777135760139006525652319754650249024631321344126610074238975
    // let q: BigInt = BigInt::from_str_radix(
    //     "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F",
    //     16
    // ).unwrap();
    // println!("q: {:?}", q);

    // The generator (base point)
    // 286650441496909734516720688912544350032790572785058722254415355376215376009112
    let g: &Secp256k1Point = ECPoint::generator();
    // println!("g: {:?}", BigInt::from_bytes(&g.serialize_compressed()));

    (
        q.clone(), 
        g.clone()
    )
}

pub fn get_secp256r1_info() -> (BigInt, Secp256r1Point) {

    // The group order p
    // FFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
    // 115792089210356248762697446949407573529996955224135760342422259061068512044369
    let q: &BigInt = Secp256r1Scalar::group_order();
    // println!("order: {:?}", q);

    // // The prime
    // // FFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF
    // // 115792089210356248762697446949407573530086143415290314195533631308867097853951
    // let q: BigInt = BigInt::from_str_radix(
    //     "FFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF",
    //     16
    // ).unwrap();
    // println!("q: {:?}", q);

    // The generator (base point)
    // 036B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296
    // 395815829005855038029765540278861637762572903522963440114216832740821793555094
    let g: &Secp256r1Point = ECPoint::generator();
    // println!("g: {:?}", BigInt::from_bytes(&g.serialize_compressed()));

    (
        q.clone(), 
        g.clone()
    )
}