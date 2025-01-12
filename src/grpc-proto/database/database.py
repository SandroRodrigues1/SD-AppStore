import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os 

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 16308))  
DB_NAME = os.getenv("DB_NAME", "defaultdb")
DB_USER = os.getenv("DB_USER", "avnadmin")
DB_PASSWORD = os.getenv("DB_PASSWORD")

load_dotenv()

def create_connection():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        if connection.is_connected():
            print("Conexão bem-sucedida ao MySQL")
            return connection
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None


def insert_product(cursor, product):
    query = """INSERT INTO products (name, price, description, image)
               VALUES (%s, %s, %s, %s)"""
    cursor.execute(query, product)

products = [
    ("Contoso Catnip's Friend", 9.99, "Watch your feline friend embark on a fishing adventure with Contoso Catnip's Friend toy. Packed with irresistible catnip and dangling fish lure.", "/catnip.jpg"),
    ("Salty Sailor's Squeaky Squid", 6.99, "Let your dog set sail with the Salty Sailor's Squeaky Squid. This interactive toy provides hours of fun, featuring multiple squeakers and crinkle tentacles.", "/squid.jpg"),
    ("Mermaid's Mice Trio", 12.99, "Entertain your kitty with the Mermaid's Mice Trio. These adorable plush mice are dressed as mermaids and filled with catnip to captivate their curiosity.", "/mermaid.jpg"),
    ("Ocean Explorer's Puzzle Ball", 11.99, "Challenge your pet's problem-solving skills with the Ocean Explorer's Puzzle Ball. This interactive toy features hidden compartments and treats, providing mental stimulation and entertainment.", "/ocean.jpg"),
    ("Pirate Parrot Teaser Wand", 8.99, "Engage your cat in a playful pursuit with the Pirate Parrot Teaser Wand. The colorful feathers and jingling bells mimic the mischievous charm of a pirate's parrot.", "/pirate.jpg"),
    ("Seafarer's Tug Rope", 14.99, "Tug-of-war meets nautical adventure with the Seafarer's Tug Rope. Made from marine-grade rope, it's perfect for interactive play and promoting dental health in dogs.", "/tug.jpg"),
    ("Seashell Snuggle Bed", 19.99, "Give your furry friend a cozy spot to curl up with the Seashell Snuggle Bed. Shaped like a seashell, this plush bed provides comfort and relaxation for cats and small dogs.", "/bed.jpg"),
    ("Nautical Knot Ball", 7.99, "Unleash your dog's inner sailor with the Nautical Knot Ball. Made from sturdy ropes, it's perfect for fetching, tugging, and satisfying their chewing needs.", "/knot.jpg"),
    ("Contoso Claw's Crabby Cat Toy", 3.99, "Watch your cat go crazy for Contoso Claw's Crabby Cat Toy. This crinkly and catnip-filled toy will awaken their hunting instincts and provide endless entertainment.", "/crabby.jpg"),
    ("Ahoy Doggy Life Jacket", 5.99, "Ensure your furry friend stays safe during water adventures with the Ahoy Doggy Life Jacket. Designed for dogs, this flotation device offers buoyancy and visibility in style.", "/lifejacket.jpg")
]


def main():

    connection = create_connection()
    
    if connection:
        cursor = connection.cursor()
        

        for product in products:
            insert_product(cursor, product)
        

        connection.commit()
        print(f"{len(products)} produtos inseridos com sucesso.")
        

        cursor.close()
        connection.close()


if __name__ == "__main__":
    main()
