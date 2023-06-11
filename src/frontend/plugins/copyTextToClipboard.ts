export default defineNuxtPlugin(() => {
    return {
        provide: {
            copyTextToClipboard
        }
    }
})

function copyTextToClipboard(text) {
    const div = document.createElement("div")
    div.innerText = text
    document.body.appendChild(div)

    const r = document.createRange()
    r.selectNode(div)
    window.getSelection().removeAllRanges()
    window.getSelection().addRange(r)
    document.execCommand('copy')
    window.getSelection().removeAllRanges()

    document?.body?.removeChild(div)
}
