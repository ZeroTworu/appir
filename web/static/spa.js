$(document).ready(() => {
    $('#start_stop').bind('click', () => {
        let form_data = getFormData($('#send_form'));
        $.ajax({
            type: 'POST',
            url: '/wipe',
            data: JSON.stringify(form_data),
            success: (res) => {
                switch (res['status']){
                    case 'error':
                        show_errors(res['errors']);
                        break;
                    case 'started':
                        update_Status();
                        break;
                }
            },
            contentType: 'application/json',
            dataType: 'json'
        });
        return false
    })
})

function show_errors(errors) {
    for (let err of errors) {
        $('#logs').append(`<div class="ERROR">${err}</div>`)
    }
}

function update_Status() {
    const user_id = $('#user_id').val()
    setInterval(() => {
        $.getJSON(`/status?user_id=${user_id}`, (res) => {
            console.log(res);
            if (res['log']) {
                const log = `<div class="${res['log']['level']}">${res['log']['msg']}</div>`;
                $('#logs').append(log)
            }
        })
    }, 1000)
}

function getFormData(form){
    const unindexed_array = form.serializeArray();
    const indexed_array = {};

    $.map(unindexed_array, (n, i) => {
        indexed_array[n['name']] = n['value'];
    });

    return indexed_array;
}