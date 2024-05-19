function setupSection(addButtonId, containerId, maxEntries, entryHtml, sectionCountId) {
    const addButton = document.getElementById(addButtonId);
    const container = document.getElementById(containerId);
    let count = 1;  // Start from 1 for easier management

    // Create or update a hidden input to keep track of the count for this section
    let sectionCountInput = document.createElement('input');
    sectionCountInput.type = 'hidden';
    sectionCountInput.id = sectionCountId;
    sectionCountInput.name = sectionCountId;
    sectionCountInput.value = '0'; // Initialize with 0, will update dynamically
    container.appendChild(sectionCountInput);

    addButton.addEventListener('click', function () {
        if (count <= maxEntries) {
            const div = document.createElement('div');
            div.innerHTML = entryHtml.replace(/{{count}}/g, count);
            div.innerHTML += '<button type="button" class="removeBtn">Remove</button>';
            container.insertBefore(div, addButton);

            const removeBtn = div.querySelector('.removeBtn');
            removeBtn.addEventListener('click', function () {
                div.remove();
                count--;  // Decrement to keep track of how many are still present
                sectionCountInput.value = count - 1; // Update hidden count
            });

            count++;
            sectionCountInput.value = count - 1; // Update hidden count
        } else {
            alert(`You can add up to ${maxEntries} entries only.`);
        }
    });
}

document.addEventListener('DOMContentLoaded', function () {
    // Setup Work Experience Section
    setupSection('addWorkExperienceBtn', 'workExperienceContainer', 10, `
    <label for="companyName{{count}}">Company Name:</label>
    <input type="text" id="companyName{{count}}" name="companyName{{count}}" required><br>
    <label for="city{{count}}">City and Country:</label>
    <input type="text" id="city{{count}}" name="city{{count}}"><br>
    <label for="role{{count}}">Role:</label>
    <input type="text" id="role{{count}}" name="role{{count}}"><br>
    <label for="roleDescription{{count}}">Role Description:</label>
    <textarea id="roleDescription{{count}}" name="roleDescription{{count}}"></textarea><br>
    <div class="date-inputs">
        <label for="startMonth{{count}}">Start:</label>
        <input type="text" id="startMonth{{count}}" name="startMonth{{count}}" placeholder="Month"><br>
        <label for="startYear{{count}}">/</label>
        <input type="text" id="startYear{{count}}" name="startYear{{count}}" placeholder="Year">
    </div>
    <div class="date-inputs">
        <label for="endMonth{{count}}">End:</label>
        <input type="text" id="endMonth{{count}}" name="endMonth{{count}}" placeholder="Month"><br>
        <label for="endYear{{count}}">/</label>
        <input type="text" id="endYear{{count}}" name="endYear{{count}}" placeholder="Year">
    </div>
    <div>
        <input type="checkbox" id="current{{count}}" name="current{{count}}" value="working">
        <label for="current{{count}}">I am working here currently.</label>
    </div>
`, 'experienceCount');


    // Setup Education Section
    setupSection('addEducation', 'educationContainer', 10, `
    <label for="institutionName{{count}}">Institution Name:</label>
    <input type="text" id="institutionName{{count}}" name="institutionName{{count}}" required><br>
    <label for="cityEdu{{count}}">City and Country:</label>
    <input type="text" id="cityEdu{{count}}" name="cityEdu{{count}}"><br>
    <label for="degree{{count}}">Degree:</label>
    <input type="text" id="degree{{count}}" name="degree{{count}}"><br>
    <div class="date-inputs">
        <label for="startMonth{{count}}">Start:</label>
        <input type="text" id="startMonth{{count}}" name="startMonth{{count}}" placeholder="Month">
        <label for="startYear{{count}}">/</label>
        <input type="text" id="startYear{{count}}" name="startYear{{count}}" placeholder="Year">
    </div>
    <div class="date-inputs">
        <label for="endMonth{{count}}">Completed: </label>
        <input type="text" id="endMonth{{count}}" name="endMonth{{count}}" placeholder="Month">
        <label for="endYear{{count}}">/</label>
        <input type="text" id="endYear{{count}}" name="endYear{{count}}" placeholder="Year">
    </div>
`, 'educationCount');

    // Setup Certifications and Awards Section
    setupSection('addCertificate', 'certificatesContainer', 10, `
    <label for="certificateName{{count}}">Certificate Name:</label>
    <input type="text" id="certificateName{{count}}" name="certificateName{{count}}" required><br>
    <label for="issuingOrg{{count}}">Issuing Organization:</label>
    <input type="text" id="issuingOrg{{count}}" name="issuingOrg{{count}}"><br>
    <div class="date-inputs">
        <label for="startMonth{{count}}">Issue Month:</label>
        <input type="text" id="startMonth{{count}}" name="startMonth{{count}}" placeholder="Month">
        <input type="text" id="startYear{{count}}" name="startYear{{count}}" placeholder="Year">
    </div>
`, 'certificateCount');

    // Setup Projects Section
    setupSection('addProject', 'projectsContainer', 10, `
        <label for="projectTitle{{count}}">Project Title:</label>
        <input type="text" id="projectTitle{{count}}" name="projectTitle{{count}}" required><br>
        <label for="projectDescription{{count}}">Project Description:</label>
        <textarea id="projectDescription{{count}}" name="projectDescription{{count}}"></textarea>
        `, 'projectCount');

    // Setup Reference Section
    setupSection('addReference', 'referenceContainer', 10, `
    <label for="referenceName{{count}}">Reference Name:</label>
    <input type="text" id="referenceName{{count}}" name="referenceName{{count}}" required><br>
    <label for="referenceTitle{{count}}">Contact Title:</label>
    <input type="text" id="referenceTitle{{count}}" name="referenceTitle{{count}}"><br>
    <label for="referenceCompany{{count}}">Reference Company:</label>
    <input type="text" id="referenceCompany{{count}}" name="referenceCompany{{count}}"></textarea><br>
    <label for="referenceContact{{count}}">Contact Information:</label>
    <input type="text" id="referenceContact{{count}}" name="referenceContact{{count}}"><br>
`, 'referenceCount');
});
