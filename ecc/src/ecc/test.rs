use curv::BigInt;

use curv::elliptic::curves::ECScalar;
use curv::elliptic::curves::ECPoint;

use curv::elliptic::curves::secp256_k1::Secp256k1Scalar;
use curv::elliptic::curves::secp256_k1::Secp256k1Point;

pub fn ecc_secp256k1_sha256(iter: u128) {

    let mut total_chkg_time: u128 = 0;
    let mut total_chash_time: u128 = 0;
    let mut total_chcheck_time: u128 = 0;
    let mut total_chadapt_time: u128 = 0;

    for _ in 0..iter {
        // q: group order
        // g: generator / base point
        let (q, g) = super::curves::get_secp256k1_info();

        // println!("========== CHKG ==========");
        let (chkg, chkg_time) = super::chkg::CHKG::chkg_secp256k1(
            q.clone(), 
        );
        // println!("CHKG: {:?}", chkg);
        
        // println!("========== CHASH ==========");
        let m: BigInt = BigInt::from(5);
        let (chash, chash_time) = super::chash::CHASH::chash_secp256k1_sha256(
            q.clone(), 
            chkg.pk.clone(), 
            m.clone()
        );
        // println!("CHASH: {:?}", chash);

        // println!("========== CHCHECK ==========");
        // let chcheck = super::chcheck::chcheck_secp256k1_sha256(
        //     q.clone(), 
        //     chkg.pk.clone(), 
        //     m.clone(), 
        //     chash.h.clone(), 
        //     chash.r.clone()
        // );
        // println!("CHCHECK: {:?}", chcheck);

        // println!("========== CHADAPT ==========");
        let m_prime: BigInt = BigInt::from(55);
        let (chadapt, chcheck_time, chadapt_time) = super::chadapt::CHADAPT::chadapt_secp256k1_sha256(
            q.clone(), 
            chkg.pk.clone(), 
            chkg.sk.clone(), 
            m.clone(), 
            m_prime.clone(), 
            chash.h.clone(), 
            chash.r.clone()
        );
        // println!("CHADAPT: {:?}", chadapt);

        total_chkg_time += chkg_time;
        total_chash_time += chash_time;
        total_chcheck_time += chcheck_time;
        total_chadapt_time += chadapt_time;
        
    }

    println!("========== [Average {:?} time] ecc_secp256k1_sha256 ==========", iter);
    println!("Running time of CHKG: {:?} ns", (total_chkg_time/iter));
    println!("Running time of CHASH: {:?} ns", (total_chash_time/iter));
    println!("Running time of CHCheck: {:?} ns", (total_chcheck_time.clone()/iter));
    println!("Running time of CHAdapt (Include CHCheck): {:?} ns", (total_chadapt_time.clone() + total_chcheck_time.clone())/iter);
    println!("Running time of CHAdapt (Exclude CHCheck): {:?} ns", (total_chadapt_time.clone()/iter));
}