document.addEventListener("DOMContentLoaded", () => {
  const button = document.getElementById("testButton");
  if (button) {
    button.onclick = () => {
      console.log("Darwin add-in loaded.");
    };
  }
});
