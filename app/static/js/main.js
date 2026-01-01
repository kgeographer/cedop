document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("test-btn");
  const out = document.getElementById("output");

  btn.addEventListener("click", async () => {
    // your known-good test point
    const lat = 16.76618535;
    const lon = -3.00777252;

    out.textContent = "Loading…";

    try {
      const res = await fetch(`/api/signature?lat=${lat}&lon=${lon}`);
      if (!res.ok) {
        out.textContent = "No data returned";
        return;
      }
      const data = await res.json();
      out.textContent = JSON.stringify(data, null, 2);
    } catch (err) {
      out.textContent = err.toString();
    }
  });
});