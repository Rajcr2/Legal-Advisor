#### Store.py

import os
import psycopg2

# 🔽 UPLOAD Function - Handles single and multiple PDFs
def upload(pdf_input):
    def upload_single(pdf_path):
        pdf_name = os.path.basename(pdf_path).split(".pdf")[0]

        try:
            conn = psycopg2.connect(
                dbname="RAG_db_llama",
                user="postgres",
                password="rajcar18",
                host="localhost",
                port="5432"
            )
            cursor = conn.cursor()

            cursor.execute("SELECT 1 FROM legal_docs WHERE name = %s", (pdf_name,))
            if cursor.fetchone():
                print(f"⚠️ Skipping upload. '{pdf_name}' already exists.")
                cursor.close()
                conn.close()
                return

            with open(pdf_path, 'rb') as file:
                binary_data = file.read()

            insert_query = "INSERT INTO legal_docs (name, pdf_data) VALUES (%s, %s)"
            cursor.execute(insert_query, (pdf_name, psycopg2.Binary(binary_data)))
            conn.commit()

            print(f"✅ Uploaded '{pdf_name}' successfully.")
            cursor.close()
            conn.close()

        except Exception as e:
            print(f"❌ Error uploading '{pdf_path}':", e)

    if isinstance(pdf_input, str):
        upload_single(pdf_input)
    elif isinstance(pdf_input, list):
        print("📦 Starting batch upload...")
        for path in pdf_input:
            upload_single(path)
        print("✅ Batch upload completed.")
    else:
        print("❌ Invalid input. Please provide a file path or list of file paths.")


# 🔽 Example usage: Modify the paths below or automate via command line args
if __name__ == "__main__":
    pdf_files = ["BNSS.pdf"]  # Replace with your file paths
    upload(pdf_files)