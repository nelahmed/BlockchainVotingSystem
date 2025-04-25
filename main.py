import hashlib
import time
import json

class Block:
    def __init__(self, index, transactions, previous_hash, timestamp=None):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp or time.time()
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "transactions": self.transactions,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

class Blockchain:
    def __init__(self, difficulty=2):
        self.pending_votes = []
        self.chain = []
        self.voted_voters = set()
        self.difficulty = difficulty
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, [], "0")
        # Optionally run PoW on genesis too, but not required
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        return self.chain[-1]

    def add_vote(self, voter_id, candidate):
        if voter_id in self.voted_voters:
            return False
        vote = {"voter_id": voter_id, "candidate": candidate}
        self.pending_votes.append(vote)
        self.voted_voters.add(voter_id)
        return True

    def proof_of_work(self, block):
        block.nonce = 0
        computed_hash = block.compute_hash()
        target = '0' * self.difficulty
        while not computed_hash.startswith(target):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash

    def add_block(self, block, proof):
        # Verify previous hash
        if block.previous_hash != self.last_block.hash:
            return False
        # Check proof matches hash & meets difficulty
        if not (proof.startswith('0' * self.difficulty) and proof == block.compute_hash()):
            return False
        block.hash = proof
        self.chain.append(block)
        return True

    def mine(self):
        if not self.pending_votes:
            return None

        last_block = self.last_block
        new_block = Block(
            index=last_block.index + 1,
            transactions=self.pending_votes,
            previous_hash=last_block.hash
        )

        proof = self.proof_of_work(new_block)
        added = self.add_block(new_block, proof)
        if not added:
            return None

        # Only clear pending votes if block was successfully added
        self.pending_votes = []
        return new_block

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i - 1]
            if curr.previous_hash != prev.hash:
                return False
            if curr.compute_hash() != curr.hash:
                return False
            if not curr.hash.startswith('0' * self.difficulty):
                return False
        return True

    def display_chain(self):
        for block in self.chain:
            print(f"\nBlock {block.index}")
            print(f"Timestamp: {time.ctime(block.timestamp)}")
            print(f"Previous Hash: {block.previous_hash}")
            print(f"Hash: {block.hash}")
            print("Votes:")
            for vote in block.transactions:
                print(f"  - {vote['voter_id']} → {vote['candidate']}")
        print()

# ========== CLI ==========

def main():
    blockchain = Blockchain(difficulty=2)
    try:
        while True:
            print("\nDecentralized Voting System")
            print("1. Cast a vote")
            print("2. Mine votes into a block")
            print("3. View blockchain")
            print("4. Validate chain")
            print("5. Exit")

            choice = input("Select an option [1-5]: ").strip()

            if choice == '1':
                voter_id = input("Enter Voter ID: ").strip()
                candidate = input("Enter Candidate Name: ").strip()
                if blockchain.add_vote(voter_id, candidate):
                    print(f"Vote cast for {candidate}.")
                else:
                    print("Error: This voter has already voted.")

            elif choice == '2':
                block = blockchain.mine()
                if block:
                    print(f"Block {block.index} mined and added.")
                else:
                    print("No votes to mine or mining failed.")

            elif choice == '3':
                blockchain.display_chain()

            elif choice == '4':
                valid = blockchain.is_chain_valid()
                print("Blockchain is valid." if valid else "Blockchain has been tampered!")

            elif choice == '5':
                print("Goodbye!")
                break

            else:
                print("Invalid selection. Please choose 1-5.")
    except KeyboardInterrupt:
        print("\nExiting. Goodbye!")

if __name__ == "__main__":
    main()
