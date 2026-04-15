def stream_text(text):
    for word in text.split():
        yield word + " "