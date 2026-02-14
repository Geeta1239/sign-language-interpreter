<?php
if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_FILES["video"])) {
    $targetDir = "uploads/";
    $targetFile = $targetDir . basename($_FILES["video"]["name"]);

    if (move_uploaded_file($_FILES["video"]["tmp_name"], $targetFile)) {
        echo json_encode(["message" => "Upload successful!", "video_url" => $targetFile]);
    } else {
        echo json_encode(["error" => "Upload failed."]);
    }
}
