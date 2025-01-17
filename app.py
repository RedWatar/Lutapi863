import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
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

# Function to handle question submission
def submit_question():
    if not file_path_var.get():
        messagebox.showerror("File Missing", "Please select a file before submitting a question.")
        return
    
    try:
        # Get the file content
        with open(file_path_var.get(), 'r') as file:
            file_content = file.read()
        
        # Get the user question
        user_question = question_entry.get()
        
        # Permanent background prompt
        background_prompt = f"This is the user's data from 5 minutes of EEG recording: {file_name.get()}\n\nData:\n{file_content}"
        
        # Complete prompt combining the background context with the user’s question
        complete_prompt = f"{background_prompt}\n\nUser's Question: {user_question}"

        # Generate response using Groq API
        completion = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": "Assist with the following EEG data:"},
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

        # Show the response in the text box
        response_label.config(text=f"Response:\n{response_text}")

    except FileNotFoundError:
        messagebox.showerror("File Error", "The selected file could not be found.")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")

# Set up the GUI window
root = tk.Tk()
root.title("EEG Data Question Assistant")

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

response_label = tk.Label(root, text="Response will appear here.")
response_label.pack(pady=10)

# Start the GUI loop
root.mainloop()
