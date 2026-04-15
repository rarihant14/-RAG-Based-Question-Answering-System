const fileInput = document.getElementById("file");
const queryInput = document.getElementById("query");
const responseBox = document.getElementById("response");
const uploadStatus = document.getElementById("uploadStatus");
const streamState = document.getElementById("streamState");
const uploadBtn = document.getElementById("uploadBtn");
const chatBtn = document.getElementById("chatBtn");

function setStatus(element, message, tone = "") {
    element.textContent = message;
    element.className = tone ? `status-line ${tone}` : "status-line";
}

function setStreamState(message, tone = "") {
    streamState.textContent = message;
    streamState.className = tone ? `stream-state ${tone}` : "stream-state";
}

fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];
    if (!file) {
        setStatus(uploadStatus, "Waiting for a document.");
        return;
    }

    setStatus(uploadStatus, `Ready to index: ${file.name}`);
});

uploadBtn.addEventListener("click", upload);
chatBtn.addEventListener("click", chat);
queryInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        event.preventDefault();
        chat();
    }
});

async function upload() {
    const file = fileInput.files[0];
    if (!file) {
        setStatus(uploadStatus, "Choose a file before indexing.", "error");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    uploadBtn.disabled = true;
    setStatus(uploadStatus, "Indexing document into the knowledge base...");

    try {
        const res = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        if (!res.ok) {
            throw new Error("Upload failed");
        }

        setStatus(uploadStatus, `${file.name} indexed successfully.`, "success");
    } catch (error) {
        setStatus(uploadStatus, "Upload failed. Check the Flask terminal for details.", "error");
    } finally {
        uploadBtn.disabled = false;
    }
}

async function chat() {
    const query = queryInput.value.trim();
    if (!query) {
        responseBox.textContent = "Enter a question to start the stream.";
        setStreamState("Prompt required", "error");
        return;
    }

    chatBtn.disabled = true;
    responseBox.textContent = "Opening stream...\n";
    setStreamState("Streaming");

    try {
        const res = await fetch("/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({query})
        });

        if (!res.ok || !res.body) {
            throw new Error("Chat failed");
        }

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let result = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) {
                break;
            }

            result += decoder.decode(value, {stream: true});
            responseBox.textContent = result;
        }

        setStreamState("Complete", "success");
    } catch (error) {
        responseBox.textContent = "The response stream failed. Check the backend logs and dependencies.";
        setStreamState("Error", "error");
    } finally {
        chatBtn.disabled = false;
    }
}
