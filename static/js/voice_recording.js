$(document).ready(function() {
    let mediaRecorder;
    let audioChunks = [];
    let stream;
    const maxRecordingTime = 60000; // Maximum recording time of 60 seconds

    $("#startRecording").click(function() {
        audioChunks = []; // Clear audio chunks before starting a new recording
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(streamObj => {
                stream = streamObj;
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.start(1000); // Record in 1-second chunks

                $("#recordingStatus").text("Recording... (Max 60 seconds)");
                $("#startRecording").hide();
                $("#stopRecording").show();

                mediaRecorder.addEventListener("dataavailable", function(event) {
                    audioChunks.push(event.data);
                });

                // Automatically stop recording after maxRecordingTime
                setTimeout(stopRecording, maxRecordingTime);
            })
            .catch(error => {
                console.error("Error accessing microphone:", error);
                $("#recordingStatus").text("Error: Unable to access microphone. Please check your browser settings.");
                $("#recordingStatus").removeClass("text-success").addClass("text-danger");
            });
    });

    function stopRecording() {
        if (mediaRecorder && mediaRecorder.state !== "inactive") {
            mediaRecorder.stop();
            $("#startRecording").show();
            $("#stopRecording").hide();
            $("#recordingStatus").text("Processing...");

            mediaRecorder.addEventListener("stop", function() {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                const formData = new FormData();
                formData.append("audio", audioBlob, "recording.wav");

                $.ajax({
                    url: "/add_voice_memory",
                    type: "POST",
                    data: formData,
                    processData: false,
                    contentType: false,
                    timeout: 120000, // Set timeout to 2 minutes
                    success: function(response) {
                        console.log("Server response:", response);
                        if (response.success) {
                            $("#recordingStatus").text(response.message);
                            $("#recordingStatus").removeClass("text-danger").addClass("text-success");
                        } else {
                            $("#recordingStatus").text("Error: " + response.message);
                            $("#recordingStatus").removeClass("text-success").addClass("text-danger");
                        }
                        audioChunks = [];
                    },
                    error: function(jqXHR, textStatus, errorThrown) {
                        console.error("AJAX Error:", textStatus, errorThrown);
                        console.error("Response Text:", jqXHR.responseText);
                        let errorMessage = "An error occurred while processing the voice memory. ";
                        if (textStatus === "timeout") {
                            errorMessage += "The request timed out. ";
                        }
                        errorMessage += "Please check the console for details.";
                        $("#recordingStatus").text(errorMessage);
                        $("#recordingStatus").removeClass("text-success").addClass("text-danger");
                        audioChunks = [];
                    },
                    xhr: function() {
                        var xhr = new window.XMLHttpRequest();
                        xhr.upload.addEventListener("progress", function(evt) {
                            if (evt.lengthComputable) {
                                var percentComplete = evt.loaded / evt.total;
                                console.log("Upload progress: " + percentComplete);
                                $("#recordingStatus").text("Uploading: " + Math.round(percentComplete * 100) + "%");
                            }
                       }, false);
                       return xhr;
                    }
                });

                // Stop all tracks on the stream to release the microphone
                if (stream) {
                    stream.getTracks().forEach(track => track.stop());
                }
            });
        }
    }

    $("#stopRecording").click(stopRecording);
});
