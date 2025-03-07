const serverURL = "https://face-attendance-github-io.onrender.com";

// Load face-api.js models
async function loadModels() {
    await faceapi.nets.tinyFaceDetector.loadFromUri('/models');
    await faceapi.nets.faceLandmark68Net.loadFromUri('/models');
    await faceapi.nets.faceRecognitionNet.loadFromUri('/models');
}

// Initialize video stream for face capture
async function initVideoStream() {
    const video = document.getElementById('video');
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: {} });
        video.srcObject = stream;
    } catch (err) {
        console.error("Error accessing camera:", err);
        alert("Error accessing camera. Please ensure your camera is enabled.");
    }
}

// Capture face data
async function captureFace() {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const context = canvas.getContext('2d');

    // Draw the current video frame to the canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Detect face and extract face descriptor
    const detections = await faceapi.detectSingleFace(canvas, new faceapi.TinyFaceDetectorOptions())
        .withFaceLandmarks()
        .withFaceDescriptor();

    if (!detections) {
        alert("No face detected. Please try again.");
        return null;
    }

    // Convert face descriptor to a format suitable for storage
    const faceDescriptor = Array.from(detections.descriptor);
    return faceDescriptor;
}

// Register student with face data
async function registerStudent() {
    try {
        const username = localStorage.getItem("username");
        if (!username) {
            throw new Error("User not logged in.");
        }

        // Capture face data
        const faceDescriptor = await captureFace();
        if (!faceDescriptor) {
            return;
        }

        // Collect form data
        const name = document.getElementById('name').value;
        const rollNumber = document.getElementById('rollNumber').value;
        const father_name = document.getElementById('father_name').value;
        const mother_name = document.getElementById('mother_name').value;
        const date_of_birth = document.getElementById('date_of_birth').value;
        const category = document.getElementById('category').value;
        const gender = document.getElementById('gender').value;
        const classValue = document.getElementById('class').value;
        const academicYear = document.getElementById('academicYear').value;

        const studentData = {
            username,
            rollNumber,
            name,
            father_name,
            mother_name,
            date_of_birth,
            category,
            gender,
            class: classValue,
            academicYear,
            faceDescriptor // Include face descriptor in the payload
        };

        console.log("Sending payload:", studentData);

        // Send data to the server
        const response = await fetch(`${serverURL}/register_student`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(studentData)
        });

        const result = await response.json();
        if (response.ok) {
            alert(result.message);
            window.location.href = `student_details.html?username=${username}&rollNumber=${rollNumber}`;
        } else {
            alert(result.error || "Failed to register student.");
        }
    } catch (error) {
        console.error("Error registering student:", error);
        alert("Error connecting to server.");
    }
}

// Initialize the page
async function init() {
    await loadModels();
    await initVideoStream();

    // Add event listener for the "Capture Face" button
    document.getElementById('captureFaceBtn').addEventListener('click', captureFace);
}

// Run initialization when the page loads
init();