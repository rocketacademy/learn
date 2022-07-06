$(function () {
    const referralChannelSelect = document.getElementById('registration-form-referral-channel');
    const referralCodeFieldDiv = document.getElementById('registration_form-referral_code_field_div');
    const referralCodeFieldTextInput = document.getElementById('registration-form-referral-code')
    
    referralChannelSelect.onchange = function() {
        if (referralChannelSelect.value == 'word_of_mouth') {
            referralCodeFieldDiv.style.display = 'block';
        } else {
            referralCodeFieldDiv.style.display = 'none';
            referralCodeFieldTextInput.value = '';
        }
    }
});