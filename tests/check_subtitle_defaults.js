// Run after prepare_stremio_tv.py, using the pinned tree's existing TypeScript.
// Exercises the actual prepared subtitle hook with fixture tracks and React hooks.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = path.resolve(__dirname, '../.private/stremio-tv-src');
const ts = require(path.join(source, 'node_modules/typescript'));

function fixture() {
    const slots = [];
    let index = 0, pending = [], requests = [], fetchImpl;
    const same = (a, b) => a && b && a.length === b.length && a.every((v, i) => Object.is(v, b[i]));
    const react = {
        useRef(value) {const i = index++; return slots[i] ||= {current: value};},
        useState(value) {
            const i = index++;
            slots[i] ||= {value};
            return [slots[i].value, value => {slots[i].value = value;}];
        },
        useMemo(fn, deps) {
            const i = index++;
            if (!slots[i] || !same(slots[i].deps, deps)) slots[i] = {deps, value: fn()};
            return slots[i].value;
        },
        useCallback(fn, deps) {return react.useMemo(() => fn, deps);},
        useEffect(fn, deps) {
            const i = index++;
            if (!slots[i] || !same(slots[i].deps, deps)) {
                const previous = slots[i];
                slots[i] = {deps};
                pending.push(() => {previous?.cleanup?.(); slots[i].cleanup = fn();});
            }
        },
    };
    const common = {
        CONSTANTS: {DEFAULT_SUBTITLES_LANGUAGE: 'eng', SUBTITLES_SIZES: [100]},
        languages: {find: value => ({code: ({en: 'eng', eng: 'eng', fr: 'fra', fra: 'fra'})[value]})},
        useToast: () => ({show() {}}), useInterval: () => ({cancel() {}, start() {}}),
        useTimeout: () => ({cancel() {}, start() {}}), useFileDropListener() {}, useShortcut() {},
    };
    let defaultHook;
    const load = (code, filename) => {
        const module = {exports: {}};
        vm.runInNewContext(code, {
            module, exports: module.exports, AbortController, setTimeout, clearTimeout,
            fetch: (...args) => {requests.push(args); return fetchImpl(...args);},
            window: {addEventListener() {}, removeEventListener() {}},
            document: {addEventListener() {}, removeEventListener() {}},
            require(name) {
                if (name === 'react') return react;
                if (name === 'react-i18next') return {useTranslation: () => ({t: x => x})};
                if (name === 'stremio/common') return common;
                if (name === './useTVSubtitleDefault') return defaultHook;
                if (name === './subtitleDelay') return {};
                throw new Error(name);
            },
        }, {filename});
        return module.exports;
    };
    defaultHook = load(fs.readFileSync(path.resolve(__dirname, '../client/useTVSubtitleDefault.js'), 'utf8'), 'useTVSubtitleDefault.js');
    const hook = load(ts.transpileModule(fs.readFileSync(path.join(source, 'src/routes/Player/useSubtitles.ts'), 'utf8'), {
        compilerOptions: {module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020},
    }).outputText, 'useSubtitles.js').default;
    const calls = [];
    const track = {id: 'english', lang: 'eng'};
    const video = {
        state: {stream: {}, subtitlesTracks: [track], extraSubtitlesTracks: [],
            selectedSubtitlesTrackId: null, selectedExtraSubtitlesTrackId: null},
        setSubtitlesTrack(id) {calls.push(['embedded', id]); video.state.selectedSubtitlesTrackId = id; video.state.selectedExtraSubtitlesTrackId = null;},
        setExtraSubtitlesTrack(id) {calls.push(['external', id]); video.state.selectedExtraSubtitlesTrackId = id; video.state.selectedSubtitlesTrackId = null;},
        events: {on() {}, off() {}}, addExtraSubtitlesTracks() {},
        setSubtitlesDelay() {}, setSubtitlesSize() {}, setSubtitlesOffset() {},
    };
    const args = {video, player: {streamState: {subtitlesEnabled: true}},
        settings: {subtitlesLanguage: 'eng'}, streamStateChanged() {}, closeSubtitlesMenu() {}};
    return {
        args, calls, requests, track,
        respond(enabled) {fetchImpl = async () => ({ok: true, json: async () => ({subtitles_default_on: enabled})});},
        defer() {let resolve; fetchImpl = () => new Promise(r => {resolve = r;}); return enabled => resolve({ok: true, json: async () => ({subtitles_default_on: enabled})});},
        fail() {fetchImpl = async () => {throw new Error('offline');};},
        render() {index = 0; const result = hook(args); const effects = pending; pending = []; effects.forEach(fn => fn()); return result;},
        dispose() {slots.forEach(slot => slot?.cleanup?.());},
    };
}
const settle = () => new Promise(resolve => setImmediate(resolve));

(async () => {
    const f = fixture();
    f.respond(false); f.render();
    assert.equal(f.args.video.state.selectedSubtitlesTrackId, null, 'Wait for the default before selecting captions');
    await settle(); f.render();
    assert.equal(f.args.video.state.selectedSubtitlesTrackId, null, 'Off overrides a saved On choice');
    let menu = f.render().subtitlesMenuProps;
    menu.onSubtitlesTrackSelected(f.track); f.render();
    assert.equal(f.args.video.state.selectedSubtitlesTrackId, 'english', 'Manual On works with default Off');
    assert.equal(f.requests.length, 1, 'No repeated fetch or reset during playback');
    f.args.video.state.stream = {}; f.render(); await settle(); f.render();
    assert.equal(f.args.video.state.selectedSubtitlesTrackId, null, 'Next episode returns to default Off');
    f.respond(true); f.args.player.streamState = {subtitlesEnabled: false};
    f.args.settings.subtitlesLanguage = null; f.args.video.state.stream = {};
    f.render(); await settle(); f.render();
    assert.equal(f.args.video.state.selectedSubtitlesTrackId, 'english', 'On overrides saved Off and falls back to English');
    menu = f.render().subtitlesMenuProps; menu.onSubtitlesTrackSelected(null); f.render();
    assert.equal(f.args.video.state.selectedSubtitlesTrackId, null, 'Manual Off remains off with default On');
    f.args.video.state.stream = {}; f.args.video.state.subtitlesTracks = []; f.args.video.state.extraSubtitlesTracks = [];
    f.render(); await settle(); f.render();
    assert.equal(f.args.video.state.selectedSubtitlesTrackId, null, 'Missing tracks do not produce a selection');
    f.args.video.state.extraSubtitlesTracks = [{id: 'external-fr', lang: 'fra'}];
    f.args.settings.subtitlesLanguage = 'fra'; f.render();
    assert.equal(f.args.video.state.selectedExtraSubtitlesTrackId, 'external-fr', 'Late external tracks use the configured language');
    f.fail(); f.args.video.state.stream = {}; f.render(); await settle(); f.render();
    assert.equal(f.args.video.state.selectedExtraSubtitlesTrackId, 'external-fr', 'Network errors use the last good default');
    f.dispose();

    const race = fixture();
    const completeOld = race.defer(); race.render();
    race.respond(false); race.args.video.state.stream = {}; race.render(); await settle(); race.render();
    completeOld(true); await settle(); race.render();
    assert.equal(race.args.video.state.selectedSubtitlesTrackId, null, 'Stale stream response cannot replace the current default');
    race.dispose();
    console.log('Subtitle hook checks passed: defaults, saved choices, manual overrides, next episodes, late tracks, fetch failure and stale responses.');
})().catch(error => {console.error(error); process.exitCode = 1;});
