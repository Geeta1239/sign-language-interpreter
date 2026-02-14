// 🎬 Smooth Page Load Animation
document.addEventListener("DOMContentLoaded", () => {
    document.body.style.opacity = "1";
    document.body.style.transition = "opacity 0.5s ease-in-out";
});

// 🔄 Clear Text Button Animation
function clearText() {
    let textElement = document.getElementById("recognized_text");
    textElement.classList.add("fade-out");

    setTimeout(() => {
        textElement.innerText = "Waiting for signs...";
        textElement.classList.remove("fade-out");
    }, 500);

    fetch('/clear_text', { method: 'POST' });
}

// 🔄 Update Recognized Text with Animation
function updateText() {
    fetch('/get_text')
        .then(response => response.text())
        .then(text => {
            let textElement = document.getElementById('recognized_text');

            if (textElement.innerText !== text) {
                textElement.classList.add("fade-in");
                textElement.innerText = text;
                
                setTimeout(() => textElement.classList.remove("fade-in"), 500);
            }
        });
}

setInterval(updateText, 1000);

// 📹 Text to Sign Animation
function convertToSign() {
    let text = document.getElementById("textInput").value;
    let loader = document.getElementById("loader");
    loader.style.display = "block"; // Show loader

    fetch("http://127.0.0.1:5000/text_to_sign", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: text })
    })
    .then(response => {
        if (!response.ok) throw new Error("Failed to get video");
        return response.blob();
    })
    .then(blob => {
        let videoUrl = URL.createObjectURL(blob);
        document.getElementById("signVideo").src = videoUrl;
        loader.style.display = "none"; // Hide loader
    })
    .catch(error => {
        console.error("Error:", error);
        loader.style.display = "none"; // Hide loader
    });
}

// Theme of Webpage
document.addEventListener("DOMContentLoaded", function () {
    const themeToggle = document.getElementById("theme-toggle");

    // Check and apply saved theme preference
    if (localStorage.getItem("theme") === "dark") {
        document.body.classList.add("dark-mode");
    }

    // Theme toggle functionality
    themeToggle.addEventListener("click", () => {
        document.body.classList.toggle("dark-mode");

        // Save theme preference to localStorage
        if (document.body.classList.contains("dark-mode")) {
            localStorage.setItem("theme", "dark");
        } else {
            localStorage.setItem("theme", "light");
        }
    });
});



function updateText() {
    fetch('/get_text')
        .then(response => response.text())
        .then(text => {
            document.getElementById('recognized_text').innerText = text;

            // Add glow effect when sign is detected
            let videoContainer = document.querySelector('.video-container');
            if (text.trim() !== "Waiting for signs...") {
                videoContainer.classList.add('detecting');
            } else {
                videoContainer.classList.remove('detecting');
            }
        });
}

function showProgress() {
    let progress = document.getElementById("progressBar");
    progress.style.width = "100%";
}

document.addEventListener("DOMContentLoaded", () => {
    let username = localStorage.getItem("username") || "User";
    document.getElementById("username").innerText = username;
});




