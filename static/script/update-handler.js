document.addEventListener('DOMContentLoaded', function() {
    // Function to add a new section (work experience or education)
    function addSection(containerId, className, countName, fields) {
        const container = document.getElementById(containerId);
        const countElement = document.getElementById(countName);
        const newIdx = parseInt(countElement.value, 10) + 1; // Update index based on current count
        const newDiv = document.createElement('div');
        newDiv.className = className;
        let innerHTML = '';

        // Loop through fields to dynamically create form inputs
        fields.forEach(field => {
            innerHTML += `<label for="${field.name}${newIdx}">${field.label}</label>`;
            if (field.type === 'textarea') {
                innerHTML += `<textarea id="${field.name}${newIdx}" name="${field.name}${newIdx}"></textarea><br>`;
            } else if (field.type === 'checkbox') {
                innerHTML += `<input type="checkbox" id="${field.name}${newIdx}" name="${field.name}${newIdx}" value="${field.value}"><label for="${field.name}${newIdx}">${field.label}</label><br>`;
            } else {
                innerHTML += `<input type="${field.type}" id="${field.name}${newIdx}" name="${field.name}${newIdx}"><br>`;
            }
        });

        innerHTML += `<button type="button" class="removeBtn" onclick="removeSection(this, '${className}', '${countName}')">Remove</button>`;
        newDiv.innerHTML = innerHTML;
        container.appendChild(newDiv);
        countElement.value = newIdx;  // Update the count value
    }

    // Function to remove a section
    function removeSection(element, className, countName) {
        const section = element.closest('.' + className);
        if (section) {
            section.remove(); // Remove the section
            const container = section.parentNode;
            const countElement = document.getElementById(countName);
            countElement.value = container.querySelectorAll('.' + className).length; // Update the count after removal
        }
    }

    // Event Listener for Adding Work Experience Sections
    document.getElementById('addWorkExperienceBtn').addEventListener('click', function() {
        addSection('workExperienceContainer', 'work-experience', 'experienceCount', [
            { label: 'Company Name:', name: 'companyName', type: 'text' },
            { label: 'City and Country:', name: 'city', type: 'text' },
            { label: 'Role:', name: 'role', type: 'text' },
            { label: 'Role Description:', name: 'roleDescription', type: 'textarea' },
            { label: 'Start Month:', name: 'startMonth', type: 'text' },
            { label: 'Start Year', name: 'startYear', type: 'text' },
            { label: 'End Month:', name: 'endMonth', type: 'text' },
            { label: 'End Year:', name: 'endYear', type: 'text' },
            { label: 'I am working here currently.', name: 'current', type: 'checkbox', value: 'working' }
        ]);
    });

    // Event Listener for Adding Education Sections
    document.getElementById('addEducationBtn').addEventListener('click', function() {
        addSection('educationContainer', 'education-entry', 'educationCount', [
            { label: 'Institution Name:', name: 'institutionName', type: 'text' },
            { label: 'City and Country:', name: 'cityEdu', type: 'text' },
            { label: 'Degree:', name: 'degree', type: 'text' },
            { label: 'Start Month:', name: 'startMonthEdu', type: 'text' },
            { label: 'Start Year:', name: 'startYearEdu', type: 'text' },
            { label: 'End Month:', name: 'endMonthEdu', type: 'text' },
            { label: 'End Year:', name: 'endYearEdu', type: 'text' }
        ]);
    });

        // Handlers for adding specific sections
        document.getElementById('addCertificate').addEventListener('click', function() {
            addSection('certificatesContainer', 'certificate-entry', 'certificateCount', [
                { label: 'Certificate Name:', name: 'certificateName', type: 'text' },
                { label: 'Issuing Organization:', name: 'issuingOrg', type: 'text' },
                { label: 'Issue Month:', name: 'issueMonth', type: 'text' },
                { label: 'Issue Year:', name: 'issueYear', type: 'text' }
            ]);
        });
    
        document.getElementById('addProject').addEventListener('click', function() {
            addSection('projectsContainer', 'project-entry', 'projectCount', [
                { label: 'Project Title:', name: 'projectTitle', type: 'text' },
                { label: 'Description:', name: 'projectDescription', type: 'textarea' }
            ]);
        });
    
        document.getElementById('addReference').addEventListener('click', function() {
            addSection('referenceContainer', 'reference-entry', 'referenceCount', [
                { label: 'Reference Name:', name: 'referenceName', type: 'text' },
                { label: 'Reference Title:', name: 'referenceTitle', type: 'text' },
                { label: 'Company:', name: 'referenceCompany', type: 'text' },
                { label: 'Contact Information:', name: 'referenceContact', type: 'text' }
            ]);
        });
});

// Function to remove a section
// Function to remove a section
function removeSection(element, className, countName) {
    const section = element.closest('.' + className);
    if (section) {
        const container = section.parentNode;
        section.remove(); // Remove the section from DOM
        const countElement = document.getElementById(countName);
        countElement.value = container.querySelectorAll('.' + className).length; // Recalculate the number of sections
    }
}