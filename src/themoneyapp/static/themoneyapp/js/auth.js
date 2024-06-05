window.addEventListener("DOMContentLoaded", () => {
  document
    .querySelectorAll(".allauth-form-container a")
    .forEach((element) => element.classList.add("text-primary-700", "hover:underline", "dark:text-primary-500"));
});
