import { seriesLoadScripts, loadLinks, $$ } from '../../utils/util'


// Dynamically load dependent scripts and styles
const dependScripts = [
    // 'expendPlugins/chart/chartmix.umd.min.js',
    'http://localhost:3000/expendPlugins/chart/chartmix.umd.min.js',
]

const dependLinks = [
    // 'expendPlugins/chart/chartmix.css',
    'http://localhost:3000/expendPlugins/chart/chartmix.css',
]

// Initialize the chart component
function print(data, isDemo) {
    loadLinks(dependLinks);

    seriesLoadScripts(dependScripts, null, function () {
        
    });
}



export { print }
