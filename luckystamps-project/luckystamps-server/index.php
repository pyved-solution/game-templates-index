<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multidimensional Array Example</title>
</head>
<body>
    <h1>Multidimensional Array</h1>
    <button id="generate-array-button">Generate Random Array</button>
    <br>
    <div id="data-container"></div>

    <script>
     const generateArrayButton = document.getElementById("generate-array-button");
const dataContainer = document.getElementById("data-container");
const creditsDisplay = document.createElement("p"); // Add element for credits

generateArrayButton.addEventListener("click", async () => {
  try {
    const response = await fetch("./oui.php");
    if (!response.ok) {
      throw new Error(`API request failed with status ${response.status}`);
    }
    console.log(response)
    const data = await response.json();
    dataContainer.innerHTML = ""; // Clear previous output

    // Extract data and credits from response
    const arrayData = data.data;
    const credits = data.credits;

    // Display the array data
    arrayData.forEach(row => {
      const rowElement = document.createElement("p");
      rowElement.textContent = row.join(" ");
      dataContainer.appendChild(rowElement);
    });

    // Display the credits
    creditsDisplay.textContent = `Credits: ${credits}`;
    dataContainer.appendChild(creditsDisplay);
  } catch (error) {
    console.error("Error:", error);
    dataContainer.textContent = "Error generating array";
  }
});

    </script>
</body>
</html>
