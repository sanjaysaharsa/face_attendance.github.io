document.addEventListener("DOMContentLoaded", async () => {
    const serverURL = "https://face-attendance-github-io.onrender.com";

    // Load face-api.js models from the 'weights' folder
    async function loadModels() {
        try {
            console.log("Loading face-api.js models...");
            await faceapi.nets.ssdMobilenetv1.loadFromUri('/weights');
            await faceapi.nets.faceLandmark68Net.loadFromUri('/weights');
            await faceapi.nets.faceRecognitionNet.loadFromUri('/weights');
            console.log("✅ Face models loaded successfully!");
        } catch (error) {
            console.error("⚠️ Error loading face models:", error);
            alert("Error loading face models. Please check the console for details.");
        }
    }

    // Initialize video stream for face capture
    async function initVideoStream() {
        const video = document.getElementById('video');
        if (!video) {
            console.error("Video element not found.");
            return;
        }

        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: {} });
            video.srcObject = stream;
            console.log("✅ Camera stream initialized successfully!");
        } catch (err) {
            console.error("⚠️ Error accessing camera:", err);
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

        // Detect face and extract face descriptor using SSD Mobilenet V1
        const detections = await faceapi.detectSingleFace(canvas, new faceapi.SsdMobilenetv1Options())
            .withFaceLandmarks()
            .withFaceDescriptor();

        if (!detections) {
            alert("No face detected. Please try again.");
            return null;
        }

        // Convert face descriptor to a format suitable for storage
        const faceDescriptor = Array.from(detections.descriptor);
        console.log("✅ Face descriptor captured:", faceDescriptor);
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
        await loadModels(); // Load models first
        await initVideoStream();

        // Add event listener for the "Capture Face" button
        const captureFaceBtn = document.getElementById('captureFaceBtn');
        if (captureFaceBtn) {
            captureFaceBtn.addEventListener('click', async () => {
                const faceDescriptor = await captureFace();
                if (faceDescriptor) {
                    alert("Face captured successfully!");
                }
            });
        } else {
            console.error("Capture Face button not found.");
        }

        // Add event listener for the registration form
        const registerForm = document.getElementById('registerForm');
        if (registerForm) {
            registerForm.addEventListener('submit', async (event) => {
                event.preventDefault();
                await registerStudent();
            });
        } else {
            console.error("Registration form not found.");
        }
    }

    // Run initialization when the page loads
    init();
});