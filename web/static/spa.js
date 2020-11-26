$(document).ready(() => {
    setInterval(() => {
        $.getJSON('/status', (res) => {
            if (res['log']) {
                $('#logs').append('<div class="info">' + res["log"] + '</div>')
            }
        })
    }, 1000)

})