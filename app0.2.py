import tkinter as tk
from tkinter import filedialog, messagebox
from groq import Groq

# Initialize the Groq client with your API key
client = Groq(api_key='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')

# Function to handle file selection
def browse_file():
    file_path = filedialog.askopenfilename(title="Select a File", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if file_path:
        file_name.set(file_path.split("/")[-1])  # Set the file name to display in the label
        file_label.config(text=f"File selected: {file_path}")
        file_path_var.set(file_path)  # Store the file path in a variable

# Function to read large files in chunks
def read_file_in_chunks(file_path, chunk_size=5000):
    """Read a file in manageable chunks to avoid memory and token limit issues."""
    try:
        with open(file_path, 'r') as file:
            while True:
                chunk = file.read(chunk_size)
                if not chunk:
                    break
                yield chunk
    except Exception as e:
        raise RuntimeError(f"Error reading file: {e}")

# Function to handle question submission
def submit_question():
    user_question = question_entry.get()

    if not user_question:
        messagebox.showerror("Input Error", "Please enter a question.")
        return

    if not file_path_var.get():
        # No file attached, proceed with a normal chat
        complete_prompt = f"User's Question: {user_question}"
        background_prompt = ""  # No background prompt (i.e., no EEG data)
    else:
        # File is attached, proceed with the EEG data context
        try:
            background_prompt = f"This is the user's data from 5 minutes of EEG recording: {file_name.get()}\n\nData:\n"
            file_path = file_path_var.get()
            
            # Read file in chunks and add to the background prompt
            for chunk in read_file_in_chunks(file_path):
                background_prompt += chunk
            
            complete_prompt = f"{background_prompt}\n\nUser's Question: {user_question}"

        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
            return

    # Generate response using Groq API
    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "Assist with the following EEG data:" if background_prompt else "You are a helpful assistant."},
                {"role": "user", "content": complete_prompt},
            ],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=True,
            stop=None,
        )

        # Extract and display the assistant's response
        response_text = ""
        for chunk in completion:
            response_text += chunk.choices[0].delta.content or ""

        response_label.config(text=f"Response:\n{response_text}")

    except Exception as e:
        messagebox.showerror("API Error", f"An error occurred while communicating with the API: {e}")

# Set up the GUI window
root = tk.Tk()
root.title("EEG Data Question Assistant")
root.geometry("600x400")

# Create variables for storing file path and file name
file_path_var = tk.StringVar()
file_name = tk.StringVar()

# Create and place the widgets
file_label = tk.Label(root, text="Select a file to upload")
file_label.pack(pady=10)

browse_button = tk.Button(root, text="Browse", command=browse_file)
browse_button.pack(pady=5)

question_label = tk.Label(root, text="Enter your question:")
question_label.pack(pady=10)

question_entry = tk.Entry(root, width=50)
question_entry.pack(pady=5)

submit_button = tk.Button(root, text="Submit Question", command=submit_question)
submit_button.pack(pady=10)

response_label = tk.Label(root, text="Response will appear here.", wraplength=550, justify="left")
response_label.pack(pady=10)

# Start the GUI loop
root.mainloop()
