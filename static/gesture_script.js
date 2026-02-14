// let gestureEnabled = false;
// let videoElement = null;
// let mediaStream = null;
// let lastX = null; // Store previous hand positionz

// document.addEventListener("DOMContentLoaded", function() {
//     videoElement = document.createElement("video");
//     videoElement.setAttribute("autoplay", "");
//     videoElement.setAttribute("playsinline", "");
//     videoElement.style.position = "fixed";
//     videoElement.style.top = "-1000px"; // Hide video
//     document.body.appendChild(videoElement);

//     async function startCamera() {
//         try {
//             mediaStream = await navigator.mediaDevices.getUserMedia({ video: true });
//             videoElement.srcObject = mediaStream;
//             detectGestures();
//         } catch (error) {
//             console.error("❌ Camera access denied:", error);
//         }
//     }

//     function stopCamera() {
//         if (mediaStream) {
//             let tracks = mediaStream.getTracks();
//             tracks.forEach(track => track.stop()); // Stop all video tracks
//             videoElement.srcObject = null;
//             console.log("📷 Camera stopped.");
//         }
//     }


//     async function detectHands() {
//         if (!model) {
//             console.log("⏳ Handpose model not loaded yet...");
//             return;
//         }

//         const predictions = await model.estimateHands(video);
        
//         if (predictions.length > 0) {
//             console.log("🖐 Detected Hand:", predictions);
//         } else {
//             console.log("❌ No Hands Detected");
//         }

//         requestAnimationFrame(detectHands);
//     }


//     async function detectGestures() {
//         console.log("🔄 Starting Gesture Detection...");
//         const model = await handpose.load();
//         console.log("🟢 Handpose Model Loaded");
//         detectHands();

//         setInterval(async () => {
//             if (!gestureEnabled) return;

//             const predictions = await model.estimateHands(videoElement);
//             console.log("📸 Predictions:", predictions);


//             if (predictions.length > 0) {
//                 const indexTipX = predictions[0].annotations.indexFinger[3][0];

//                 console.log(`🖐 Hand Detected! X Position: ${indexTipX}`);

//                 if (lastX !== null) {
//                     let diff = indexTipX - lastX;
//                     console.log(`↔ Swipe Distance: ${diff}px`);

//                     if (diff > 40) {  // Right Swipe
//                         console.log("➡ Swipe Right - Forward");
//                         window.history.forward();
//                         lastX = null;
//                     } else if (diff < -40) { // Left Swipe
//                         console.log("⬅ Swipe Left - Back");
//                         window.history.back();
//                         lastX = null;
//                     }
//                 }
//                 lastX = indexTipX; // Store X position
//             }
//         }, 200);
//     }


//     // Gesture Toggle Button
//     document.getElementById("gesture-toggle").addEventListener("click", function() {
//         gestureEnabled = !gestureEnabled;
//         this.innerText = gestureEnabled ? "Disable Gestures" : "Enable Gestures";

//         if (gestureEnabled) {
//             startCamera();
//         } else {
//             stopCamera();
//             lastX = null; // Reset tracking
//         }
//     });
// });


let gestureEnabled = false;
let videoElement = null;
let mediaStream = null;
let lastX = null; // Store previous hand position

document.addEventListener("DOMContentLoaded", function() {
    // Create video element for webcam feed
    videoElement = document.createElement("video");
    videoElement.setAttribute("autoplay", "");
    videoElement.setAttribute("playsinline", "");
    videoElement.style.position = "fixed";
    videoElement.style.top = "-1000px"; // Hide video
    document.body.appendChild(videoElement);

    // Initialize camera feed
    async function startCamera() {
        try {
            mediaStream = await navigator.mediaDevices.getUserMedia({ video: true });
            videoElement.srcObject = mediaStream;
        } catch (error) {
            console.error("❌ Camera access denied:", error);
        }
    }

    // Stop camera feed
    function stopCamera() {
        if (mediaStream) {
            let tracks = mediaStream.getTracks();
            tracks.forEach(track => track.stop()); // Stop all video tracks
            videoElement.srcObject = null;
            console.log("📷 Camera stopped.");
        }
    }

    // Capture a frame from the video feed and send it to the server for gesture recognition
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");


    function captureFrame() {
        if (!gestureEnabled) return;

        canvas.width = videoElement.videoWidth;
        canvas.height = videoElement.videoHeight;
        ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
        const dataUrl = canvas.toDataURL("image/jpeg");

        fetch("/process_gesture", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ image: dataUrl }),
        })
        .then((res) => res.json())
        .then((data) => {
            if (data.gesture === "open_palm") {
                window.location.href = "/sign_to_text";
            } else if (data.gesture === "point_up") {
                window.location.href = "/text_to_sign";
            } else if (data.gesture === "point_right") {
                window.location.href = "/gesture_navigation";
            } else if (data.gesture === "closed_fist") {
                gestureEnabled = false;
                alert("Gesture recognition disabled.");
            } else if (data.gesture === "go_back") {
                console.log("🔙 Gesture Detected: Going Back");
                window.history.back();  // Go back in browser history
            }
        });
    }

    
    // Capture every 1.2 seconds
    setInterval(captureFrame, 1200);

    // Gesture detection logic (Swipe detection)
    async function detectGestures() {
        console.log("🔄 Starting Gesture Detection...");
        const model = await handpose.load();
        console.log("🟢 Handpose Model Loaded");


        setInterval(async () => {
            if (!gestureEnabled) return;

            const predictions = await model.estimateHands(videoElement);
            console.log("📸 Predictions:", predictions);

            if (predictions.length > 0) {
                const indexTipX = predictions[0].annotations.indexFinger[3][0]; 

                console.log(`🖐 Hand Detected! X Position: ${indexTipX}`);

                if (lastX !== null) {
                    let diff = indexTipX - lastX;
                    console.log(`↔ Swipe Distance: ${diff}px`);

                    // Detect right swipe (move forward)
                    if (diff > 40) {
                        console.log("➡ Swipe Right - Navigate to Text to AI Avatar");
                        window.location.href = "/text_to_sign";
                        lastX = null; // Reset the X position for the next gesture
                    }
                    // Detect left swipe (move back)
                    else if (diff < -40) {
                        console.log("⬅ Swipe Left - Navigate to Sign to Text/Speech");
                        window.location.href = "/sign_to_text";
                        lastX = null; // Reset the X position for the next gesture
                    }
                }

                lastX = indexTipX; // Store X position for swipe calculation
            }
        }, 200); // 200ms interval for gesture checks
    }

    // Gesture Toggle Button
    document.getElementById("gesture-toggle").addEventListener("click", function() {
        gestureEnabled = !gestureEnabled;
        localStorage.setItem("gestureEnabled", gestureEnabled);  // Save state
        this.innerText = gestureEnabled ? "Disable Gestures" : "Enable Gestures";

        if (gestureEnabled) {
            startCamera();
            detectGestures(); // Restart detection
        } else {
            stopCamera();
            lastX = null;
        }
    });

});

if (localStorage.getItem("gestureEnabled") === "true") {
    gestureEnabled = true;
    document.getElementById("gesture-toggle").innerText = "Disable Gestures";
    startCamera();
    detectGestures();
}

