# Source code for the Chameleon Hash Paper

Implementation of the paper: Kwan Yin Chan, Liqun Chen, Yangguang Tian, and Tsz Hon Yuen: Reconstructing Chameleon Hash: Full Security and the Multi-Party Setting. In ACM AsiaCCS 2024.

```./ecc``` is the source code for ECC-based construction

```./lattice``` is the source code for lattice-based construction

## Library used
We adopt the libraries:
- [curv](https://github.com/ZenGo-X/curv) from Zengo-X for ECC component
- [sha2](https://github.com/RustCrypto/hashes) for SHA-2 hashes
- [SymPy](https://www.sympy.org/en/index.html) for lattice-based component
