document.addEventListener("DOMContentLoaded", function() {
    const input = document.querySelector("#equipment-input");
    const container = document.querySelector("#chips-container");
    const optionsInput = document.querySelector("#options-input");
    let chipsData = [];  // Array to store chip values

    function updateOptionsInput() {
        optionsInput.value = JSON.stringify(chipsData);
    }

    function createChip(chipValue) {
        const chip = document.createElement('div');
        chip.className = 'chip bg-blue-500 text-white text-sm rounded-lg px-2 py-1 mr-2';
        chip.dataset.value = chipValue;
        chip.innerHTML = `${chipValue} <span class="closebtn ml-2 cursor-pointer">×</span>`;

        // Add event listener to the close button within the chip
        chip.querySelector(".closebtn").addEventListener("click", function() {
            removeChip(chip, chipValue);
        });
        
        return chip;
    }

    function removeChip(chipElement, value) {
        chipElement.remove();
        chipsData = chipsData.filter(chip => chip.value !== value);
        updateOptionsInput();
    }

    input.addEventListener("keyup", function(event) {
        if (event.key === "Enter" && this.value.trim() !== "") {
            const chipValue = this.value.trim();
            chipsData.push({ value: chipValue });  // Add to the array

            const chip = createChip(chipValue);
            container.insertBefore(chip, this);
            
            this.value = "";
            updateOptionsInput();  // Update the hidden input every time a chip is added or removed
        }
    });
});