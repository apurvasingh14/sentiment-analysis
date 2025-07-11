import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import pickle
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Load model and vectorizer
with open("sentiment_model.pkl", "rb") as model_file:
    model = pickle.load(model_file)
with open("vectorizer.pkl", "rb") as vec_file:
    vectorizer = pickle.load(vec_file)

# Store session data
session_data = []

# Detect intent
def detect_intent(text):
    text = text.lower()
    if any(word in text for word in ["buy", "purchase", "order", "good", "very good", "fantastic", "awesome", "excellent"]):
        return "Purchase"
    elif any(word in text for word in ["return", "refund", "cancel", "bad", "not good"]):
        return "Return/Cancel"
    elif any(word in text for word in ["recommend", "suggest", "refer"]):
        return "Recommendation"
    else:
        return "General Feedback"

# Predict sentiment
def predict_sentiment():
    user_input = entry.get()
    if not user_input.strip():
        messagebox.showwarning("Input Error", "Please enter a sentence.")
        return

    vec_input = vectorizer.transform([user_input])
    prediction = model.predict(vec_input)[0]
    intent = detect_intent(user_input)

    # Store input
    session_data.append({'text': user_input, 'sentiment': prediction, 'intent': intent})

    # Update Sentiment box
    result_label.config(
        text=f"Sentiment: {prediction.capitalize()}",
        bg="#f8d7da" if prediction.lower() == "negative" else "#ffeeba",
        fg="#721c24" if prediction.lower() == "negative" else "#856404"
    )

    # Emotion box
    if prediction.lower() == "positive":
        emoji_label.config(image=positive_img)
        emoji_label.image = positive_img
        emotion_label.config(text="Emotion: Happy", bg="#d4edda", fg="green")
    else:
        emoji_label.config(image=negative_img)
        emoji_label.image = negative_img
        emotion_label.config(text="Emotion: Sad", bg="#f8d7da", fg="red")

    # Intent
    intent_label.config(text=f"Intent: {intent}", bg="#d1ecf1", fg="blue")

    # Update review count
    review_count_label.config(text=f"Reviews stored: {len(session_data)}")

    # Append to review list
    reviews_box.insert(tk.END, f"{user_input}\n")
    reviews_box.see(tk.END)

# Updated Pie Chart (Shows sentiment distribution instead of intent)
def show_pie_chart():
    for widget in chart_frame.winfo_children():
        widget.destroy()

    sentiments = [data['sentiment'].capitalize() for data in session_data]
    if not sentiments:
        return

    counts = Counter(sentiments)
    labels = list(counts.keys())  # ['Positive', 'Negative']
    sizes = list(counts.values())

    fig, ax = plt.subplots(figsize=(4, 2), dpi=100)
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=["#a8e6cf", "#ff8b94"])
    ax.axis('equal')
    fig.patch.set_facecolor('white')

    pie_canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    pie_canvas.draw()
    pie_canvas.get_tk_widget().pack()

# Draw background gradient
def draw_gradient(canvas, width, height):
    canvas.delete("gradient")
    for i in range(height):
        r = 240 - int(i / height * 100)
        g = 240 - int(i / height * 40)
        b = 255
        color = f"#{r:02x}{g:02x}{b:02x}"
        canvas.create_line(0, i, width, i, tags="gradient", fill=color)

# GUI Setup
window = tk.Tk()
window.title("Sentiment Analysis")
window.geometry("900x700")
window.minsize(600, 600)

canvas = tk.Canvas(window, highlightthickness=0)
canvas.pack(fill="both", expand=True)
canvas.bind("<Configure>", lambda e: draw_gradient(canvas, e.width, e.height))

frame = tk.Frame(canvas, bg="white", bd=2)
frame.place(relx=0.5, rely=0.5, anchor="center")

# Header
tk.Label(frame, text="Sentiment Analysis of Product Review", font=("Helvetica", 16, "bold"), bg="white").pack(pady=10)

# Input area
tk.Label(frame, text="Enter text:", font=("Helvetica", 12), bg="white").pack(pady=5)
entry = tk.Entry(frame, width=60, font=("Helvetica", 12))
entry.pack(pady=5)

# Analyze button
tk.Button(frame, text="Analyze Sentiment", command=predict_sentiment).pack(pady=10)

# Result display
result_label = tk.Label(frame, text="", font=("Helvetica", 12, "bold"), width=60)
result_label.pack(pady=5)

emotion_label = tk.Label(frame, text="", font=("Helvetica", 12, "bold"), width=60)
emotion_label.pack(pady=5)

intent_label = tk.Label(frame, text="", font=("Helvetica", 12, "bold"), width=60)
intent_label.pack(pady=5)

# Review count
review_count_label = tk.Label(frame, text="Reviews stored: 0", font=("Helvetica", 11), bg="white", fg="gray")
review_count_label.pack(pady=5)

# Emoji display
positive_img_raw = Image.open("positive.jpeg").resize((64, 64), Image.Resampling.LANCZOS)
negative_img_raw = Image.open("negative.jpeg").resize((64, 64), Image.Resampling.LANCZOS)
positive_img = ImageTk.PhotoImage(positive_img_raw)
negative_img = ImageTk.PhotoImage(negative_img_raw)
emoji_label = tk.Label(frame, bg="white")
emoji_label.pack(pady=5)

# Stored reviews
tk.Label(frame, text="Stored Reviews:", font=("Helvetica", 12, "bold"), bg="white").pack()
reviews_box = tk.Text(frame, height=5, width=65, font=("Helvetica", 10), bg="#f9f9f9", wrap="word")
reviews_box.pack(pady=5)

# Pie chart button
tk.Button(frame, text="Show Sentiment Pie Chart", command=show_pie_chart, font=("Helvetica", 11)).pack(pady=10)

# Chart frame (initially blank)
chart_frame = tk.Frame(frame, bg="white")
chart_frame.pack(pady=10)

print("Launching GUI...")
window.mainloop()
