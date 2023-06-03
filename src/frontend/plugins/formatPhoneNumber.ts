export default defineNuxtPlugin(() => {
    return {
        provide: {
            formatPhoneNumber
        }
    }
})

function formatPhoneNumber(number: string = ''): string {
    if (!number) return '';
  // Remove the optional '+' from the start if present
  number = number.startsWith('+') ? number.substring(1) : number;

  // Now construct the formatted number
    return `+${number.substring(0, 1)} (${number.substring(1, 4)}) ${number.substring(4, 7)}-${number.substring(7)}`;
}

