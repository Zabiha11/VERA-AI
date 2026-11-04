const micButton = document.getElementById("mic-button");
const stopButton = document.getElementById("stop-button");
const uploadButton = document.getElementById("upload-button");

const statusText = document.getElementById("status");
const statusDot = document.getElementById("status-dot");
const message = document.getElementById("message");
const recordingTime = document.getElementById("recording-time");

const previewSection = document.getElementById("preview-section");
const audioPreview = document.getElementById("audio-preview");
const audioInfo = document.getElementById("audio-info");
const transcribeButton = document.getElementById("transcribe-button");
const transcriptSection = document.getElementById("transcript-section");
const transcriptText = document.getElementById("transcript-text");
const transcriptDetails = document.getElementById("transcript-details");
const understandButton = document.getElementById("understand-button");
const intentResult = document.getElementById("intent-result");
const executeButton = document.getElementById("execute-button");
const actionResult = document.getElementById("action-result");
const chatMessages = document.getElementById("chatMessages");

let uploadedFilename = null;
let mediaRecorder = null;
let audioChunks = [];
let audioBlob = null;
let audioStream = null;
let startedAt = 0;
let timerId = null;
let previewUrl = null;
let isUploading = false;
let conversationId = localStorage.getItem("vera_conversation_id");

function setStatus(text, color = "#79a889") {
    statusText.textContent = text;
    statusDot.style.backgroundColor = color;
}

function showMessage(text) {
    message.textContent = text;
}

function releaseMicrophone() {
    if (audioStream) {
        audioStream.getTracks().forEach(track => track.stop());
        audioStream = null;
    }
}

function resetPreview() {
    if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
        previewUrl = null;
    }

    audioPreview.removeAttribute("src");
    audioPreview.load();
    previewSection.hidden = true;
    audioInfo.textContent = "";
}

function updateButtons() {
    const recording = mediaRecorder?.state === "recording";

    micButton.disabled = recording || isUploading;
    stopButton.disabled = !recording;
    uploadButton.disabled = !audioBlob || isUploading || recording;
    transcribeButton.disabled = !uploadedFilename || isUploading || recording;
    executeButton.disabled = isUploading || !transcriptText.textContent.trim();
}

function getSupportedMimeType() {
    const types = [
        "audio/webm;codecs=opus",
        "audio/webm",
        "audio/mp4"
    ];

    return types.find(type =>
        MediaRecorder.isTypeSupported(type)
    ) || "";
}

micButton.addEventListener("click", async () => {
    showMessage("");

    if (!navigator.mediaDevices?.getUserMedia ||
        typeof MediaRecorder === "undefined") {
        setStatus("Recording is not supported", "#c65b50");
        showMessage(
            "Use a recent browser such as Chrome or Edge. " +
            "Microphone access requires localhost or HTTPS."
        );
        return;
    }

    try {
        resetPreview();
        audioBlob = null;
        audioChunks = [];

        uploadedFilename = null;
        transcriptSection.hidden = true;
        transcriptText.textContent = "";
        transcriptDetails.textContent = "";
        intentResult.textContent = "";

        updateButtons();

        setStatus("Requesting microphone access...", "#bd9653");

        audioStream = await navigator.mediaDevices.getUserMedia({
            audio: true
        });

        const mimeType = getSupportedMimeType();

        mediaRecorder = mimeType
            ? new MediaRecorder(audioStream, { mimeType })
            : new MediaRecorder(audioStream);

        mediaRecorder.addEventListener("dataavailable", event => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        });

        mediaRecorder.addEventListener("stop", () => {
            const actualType =
                mediaRecorder.mimeType || "application/octet-stream";

            audioBlob = new Blob(audioChunks, {
                type: actualType
            });

            releaseMicrophone();

            if (audioBlob.size === 0) {
                audioBlob = null;
                setStatus("No audio recorded", "#c65b50");
                showMessage("Please record again and speak into your microphone.");
                updateButtons();
                return;
            }

            previewUrl = URL.createObjectURL(audioBlob);
            audioPreview.src = previewUrl;
            previewSection.hidden = false;

            audioInfo.textContent =
                `Format: ${audioBlob.type || "unknown"} · ` +
                `Size: ${(audioBlob.size / 1024).toFixed(1)} KB`;

            setStatus("Recording ready to upload");
            showMessage("Recording complete. Play it back or upload it.");
            updateButtons();
        });

        mediaRecorder.addEventListener("error", () => {
            clearInterval(timerId);
            timerId = null;
            releaseMicrophone();

            setStatus("Recording failed", "#c65b50");
            showMessage("The browser encountered an audio recording error.");
            updateButtons();
        });

        mediaRecorder.start();
        startedAt = Date.now();

        recordingTime.textContent = "Recording time: 0 seconds";
        setStatus("Listening...", "#c65b50");
        showMessage("Speak now. Select Stop recording when finished.");

        timerId = setInterval(() => {
            const seconds = Math.floor((Date.now() - startedAt) / 1000);
            recordingTime.textContent = `Recording time: ${seconds} seconds`;
        }, 500);

        updateButtons();

    } catch (error) {
        releaseMicrophone();

        setStatus("Microphone unavailable", "#c65b50");

        if (error.name === "NotAllowedError") {
            showMessage(
                "Microphone permission was denied. Allow microphone access " +
                "in your browser's site settings and try again."
            );
        } else if (error.name === "NotFoundError") {
            showMessage("No microphone was found. Connect or enable one.");
        } else if (error.name === "NotReadableError") {
            showMessage(
                "The microphone could not be accessed. Check whether another " +
                "application is using it."
            );
        } else {
            showMessage(`Could not start recording: ${error.message}`);
        }

        updateButtons();
    }
});

stopButton.addEventListener("click", () => {
    if (mediaRecorder?.state === "recording") {
        clearInterval(timerId);
        timerId = null;
        mediaRecorder.stop();
        setStatus("Preparing recording...", "#bd9653");
    }
});

uploadButton.addEventListener("click", async () => {
    if (!audioBlob || isUploading) {
        return;
    }

    isUploading = true;
    updateButtons();

    setStatus("Uploading audio...", "#bd9653");
    showMessage("Sending your recording to the VERA backend...");

    try {
        const extension = audioBlob.type.includes("mp4")
            ? "mp4"
            : audioBlob.type.includes("webm")
                ? "webm"
                : "bin";

        const formData = new FormData();
        formData.append("audio", audioBlob, `recording.${extension}`);

        const response = await fetch("/api/upload-audio", {
            method: "POST",
            body: formData
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Upload failed.");
        }

        uploadedFilename = result.filename;
        setStatus("Audio received by VERA");
        showMessage(
            `Upload successful! Saved ${result.filename} ` +
            `(${(result.size_bytes / 1024).toFixed(1)} KB). ` +
            "Speech recognition will be added in Part 3."
        );

    } catch (error) {
        setStatus("Upload failed", "#c65b50");
        showMessage(
            `${error.message} Check that Flask is running and try again.`
        );
    } finally {
        isUploading = false;
        updateButtons();
    }
});

const newChatButton = document.getElementById("newChatButton");

newChatButton.addEventListener("click", () => {

    conversationId = null;
    localStorage.removeItem("vera_conversation_id");

    // Clear the previous conversation display
    chatMessages.innerHTML = "";
    chatMessages.textContent = "New conversation started.";

    // Clear previous request information
    transcriptText.textContent = "";
    transcriptDetails.textContent = "";
    intentResult.textContent = "";
    actionResult.textContent = "";
    transcriptSection.hidden = true;

    uploadedFilename = null;
    audioBlob = null;

    resetPreview();
    updateButtons();

    setStatus("Ready for a new conversation");
    showMessage("VERA is ready. Start recording your next request.");

    console.log("VERA: New conversation started.");
});

transcribeButton.addEventListener("click", async () => {
    if (!uploadedFilename || isUploading) return;

    isUploading = true;
    updateButtons();
    transcriptSection.hidden = true;

    setStatus("Loading speech model...", "#bd9653");
    showMessage(
        "The first run may take longer while the model downloads. Please wait."
    );

    try {
        const response = await fetch("/api/transcribe", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                filename: uploadedFilename
            })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Transcription failed.");
        }

        transcriptText.textContent = result.text;
        transcriptDetails.textContent =
            `Language: ${result.language} · ` +
            `Confidence: ${(result.language_probability * 100).toFixed(1)}% · ` +
            `Audio duration: ${result.duration_seconds} seconds`;

        transcriptSection.hidden = false;
        setStatus("Transcription complete");
        showMessage("VERA recognized your speech locally.");

    } catch (error) {
        setStatus("Transcription failed", "#c65b50");
        showMessage(
            `${error.message} Check the Flask terminal for more details.`
        );
    } finally {
        isUploading = false;
        updateButtons();
    }
});

understandButton.addEventListener("click", async () => {
    const text = transcriptText.textContent.trim();

    if (!text || isUploading) return;

    isUploading = true;
    updateButtons();
    understandButton.disabled = true;
    intentResult.textContent = "Understanding your request...";

    try {
        const response = await fetch("/api/intent", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ text })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Classification failed.");
        }

        // Display the detected intent
        // Display how VERA will handle the request
        if (result.method === "rule") {

            intentResult.textContent =
                `Intent: ${result.intent} · Matched by rule`;

        } else if (result.method === "agent") {

            intentResult.textContent =
                "Intent: AI Agent · VERA will process this using Groq.";

        } else if (result.needs_clarification) {

            intentResult.textContent =
                "VERA needs more information to understand this request.";

        } else {

            intentResult.textContent =
                `Intent: ${result.intent}`;
        }

    } catch (error) {
        intentResult.textContent = `Error: ${error.message}`;
    } finally {
        isUploading = false;
        understandButton.disabled = false;
        updateButtons();
    }
});


executeButton.addEventListener("click", async () => {
    const text = transcriptText.textContent.trim();

    if (!text || isUploading) return;

    isUploading = true;
    updateButtons();
    actionResult.textContent = "VERA is processing your request...";

    try {
        const response = await fetch("/api/execute", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
            text: text,
            conversation_id: conversationId
        })
        });

        const result = await response.json();

        if (result.conversation_id) {
            conversationId = result.conversation_id;

            localStorage.setItem(
                "vera_conversation_id",
                conversationId
            );
        }

        if (!response.ok) {
            throw new Error(result.error || "Action failed.");
        }

        actionResult.textContent = result.response || result.message || "VERA completed the request.";

        // Refresh the displayed conversation and history
        if (conversationId) {
            await openConversation(conversationId);
        }

        await loadConversationList();

    } catch (error) {
        actionResult.textContent = `Error: ${error.message}`;
    } finally {
        isUploading = false;
        updateButtons();
    }
});

window.addEventListener("beforeunload", () => {
    clearInterval(timerId);
    releaseMicrophone();

    if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
    }
});

console.log("VERA voice recording module loaded.");

// --------------------------------------------------
// CONVERSATION HISTORY
// --------------------------------------------------

const conversationList = document.getElementById("conversationList");

async function loadConversationList() {

    if (!conversationList) return;

    try {
        const response = await fetch("/api/conversations");
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Could not load conversations.");
        }

        conversationList.innerHTML = "";

        if (result.conversations.length === 0) {
            conversationList.textContent = "No previous conversations.";
            return;
        }

        result.conversations.forEach(conversation => {

            const item = document.createElement("button");

            item.className = "conversation-item";
            item.textContent = conversation.title || "New conversation";

            item.addEventListener("click", () => {
                openConversation(conversation.id);
            });

            conversationList.appendChild(item);
        });

    } catch (error) {
        conversationList.textContent = "Could not load chat history.";
        console.error(error);
    }
}


async function openConversation(id) {

    try {
        const response = await fetch(
            `/api/conversations/${encodeURIComponent(id)}`
        );

        const result = await response.json();

        if (!response.ok) {
            throw new Error(
                result.error || "Could not open conversation."
            );
        }

        conversationId = result.conversation_id;

        localStorage.setItem(
            "vera_conversation_id",
            conversationId
        );

        // Display previous messages
        displayMessages(result.messages);

        setStatus("Previous conversation loaded");
        showMessage(`Opened: ${result.title}`);

        console.log("VERA conversation loaded.");

    } catch (error) {
        console.error("Conversation loading error:", error);
        showMessage(`Could not open conversation: ${error.message}`);
    }
}

// --------------------------------------------------
// DISPLAY CONVERSATION MESSAGES
// --------------------------------------------------

function displayMessages(messages) {

    chatMessages.innerHTML = "";

    if (!messages || messages.length === 0) {
        chatMessages.textContent = "No messages in this conversation.";
        return;
    }

    messages.forEach(msg => {

        const messageDiv = document.createElement("div");
        messageDiv.className = `chat-message ${msg.role}`;

        const roleLabel = document.createElement("strong");
        roleLabel.textContent =
            msg.role === "user" ? "You" : "VERA";

        const content = document.createElement("p");
        content.textContent = msg.content;

        messageDiv.appendChild(roleLabel);
        messageDiv.appendChild(content);

        chatMessages.appendChild(messageDiv);
    });

    chatMessages.scrollTop = chatMessages.scrollHeight;
}

loadConversationList();

console.log("VERA conversation history module loaded.");