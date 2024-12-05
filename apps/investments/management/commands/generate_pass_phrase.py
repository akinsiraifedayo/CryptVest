from mnemonic import Mnemonic

def generate_mnemonic():
    # Initialize Mnemonic with the desired language
    mnemo = Mnemonic("english")
    
    # Generate a 12-word mnemonic
    mnemonic_phrase = mnemo.generate(strength=128)  # 128 bits of entropy results in a 12-word mnemonic
    
    return mnemonic_phrase

if __name__ == "__main__":
    passphrase = generate_mnemonic()
    print(f"Generated Trust Wallet Passphrase: {passphrase}")
