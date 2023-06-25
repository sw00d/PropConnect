import AOS from "aos";
import "aos/dist/aos.css";


export default defineNuxtPlugin((app) => {
    app.AOS = AOS.init({
        once: false,
    })
});
