$(document).ready(() => {
    const start_btn = $('#start');
    const stop_btn = $('#stop');
    const sid = $('#sid').val()
    let update_interval;
    start_btn.bind('click', () => {
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
                        change_btns(true)
                        $('#logs').append('<div class="INFO">Ожидаем ответа...</div>')
                        update_interval = update_status();
                        break;
                }
            },
            contentType: 'application/json',
            dataType: 'json'
        });
        return false
    })

    stop_btn.bind('click', () => {
        $.getJSON(`/stop/${sid}`, (res) => {
            switch (res['status']) {
                case 'stopped':
                    change_btns(false)
                    $('#logs').append('<div class="INFO">Остановлено.</div>')
                    clearInterval(update_interval)
                    break;
            }
        })
        return false
    });
})

function change_btns(disable) {
    $('#start').prop('disabled', disable);
    $('#stop').prop('disabled', !disable);
}

function show_errors(errors) {
    for (let err of errors) {
        $('#logs').append(`<div class="ERROR">${err}</div>`)
    }
}

function update_status() {
    const sid = $('#sid').val()
    const logs = $('#logs');
    const handler = () => {
        $.getJSON(`/status/${sid}`, (res) => {
            for (let log of res) {
                if (logs.has(`#${log['timestamp']}`).length === 0) {
                    const log_record = `<div id="${log['timestamp']}" class="${log['level']}">${log["msg"]}</div>`;
                    logs.append(log_record)
                }
            }
        })
    }
    return setInterval(handler, 1000)

}

function getFormData(form){
    const unindexed_array = form.serializeArray();
    const indexed_array = {};

    $.map(unindexed_array, (n, i) => {
        indexed_array[n['name']] = n['value'];
    });

    return indexed_array;
}