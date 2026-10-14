const fileInput = document.querySelector("#video");
const fileLabel = document.querySelector("#file-label");
const uploadForm = document.querySelector(".upload-form");
const progress = document.querySelector("#upload-progress");

if (fileInput && fileLabel) {
  fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];
    fileLabel.textContent = file ? `${file.name} (${(file.size / 1048576).toFixed(1)} MB)` : "Choose a video to upload";
  });
}

if (uploadForm && progress) {
  uploadForm.addEventListener("submit", () => {
    progress.hidden = false;
    const button = uploadForm.querySelector('button[type="submit"]');
    if (button) {
      button.disabled = true;
      button.textContent = "Uploading… please wait";
    }
  });
}
