#!/usr/bin/env python3
"""Apply the documented TV adaptations to the pinned local Stremio source tree."""
from pathlib import Path
import difflib
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / ".private/stremio-tv-src"


def replace(path, old, new):
    value = path.read_text()
    if new in value:
        return
    if value.count(old) != 1:
        raise RuntimeError(f"Expected one patch location in {path.name}")
    path.write_text(value.replace(old, new))


def dependency_patch(path, old, new, record):
    original = path.read_text()
    if new in original:
        return
    if original.count(old) != 1:
        raise RuntimeError(f'Unexpected dependency patch location: {path.name}')
    updated = original.replace(old, new)
    temp = path.with_suffix('.js.tv-new')
    temp.write_text(updated)
    temp.replace(path)
    (ROOT / 'research/reviews' / record).write_text(''.join(difflib.unified_diff(
        original.splitlines(True), updated.splitlines(True), fromfile=path.name, tofile=path.name)))


def main():
    player = SOURCE / "src/routes/Player/Player.js"
    replace(player, 'forceTranscoding: forceTranscoding || casting,',
            "forceTranscoding: forceTranscoding || casting,\n                audioCodecs: ['aac'],\n                maxAudioChannels: 2,")
    replace(player, "const ControlBar = require('./ControlBar');", "const ControlBar = require('./ControlBar');\nconst TVRemoteBar = require('./TVRemoteBar');")
    if '<TVRemoteBar' not in player.read_text():
        replace(player, "            <Indicator\n", "            <TVRemoteBar state={video.state} menusOpen={menusOpen} active={routeFocused}\n                onPlayPause={onPlayPause} onSeek={onSeekRequested}\n                onCaptions={toggleSubtitlesMenu} onAudio={toggleAudioMenu}\n                onBrowse={() => navigate('/')} onCloseMenus={closeMenus} />\n            <Indicator\n")
    elif 'onCloseMenus={closeMenus}' not in player.read_text():
        replace(player, "onBrowse={() => navigate('/')} />", "onBrowse={() => navigate('/')} onCloseMenus={closeMenus} />")
    shutil.copyfile(ROOT / "client/TVRemoteBar.js", player.parent / "TVRemoteBar.js")
    shutil.copyfile(ROOT / 'client/useTVSubtitleDefault.js', player.parent / 'useTVSubtitleDefault.js')
    subtitles = player.parent / 'useSubtitles.ts'
    replace(subtitles, "const withFallbackLabels =", "const useTVSubtitleDefault = require('./useTVSubtitleDefault');\n\nconst withFallbackLabels =")
    replace(subtitles, '    const toast = useToast();',
            '    const toast = useToast();\n    const tvSubtitleDefault = useTVSubtitleDefault(video.state.stream);')
    replace(subtitles, '        const subtitlesEnabled = player.streamState?.subtitlesEnabled;\n\n        if (subtitlesEnabled === false || (!subtitlesEnabled && settings.subtitlesLanguage === null)) {',
            '''        const subtitlesEnabled = true;

        if (!tvSubtitleDefault.ready || !tvSubtitleDefault.enabled) {''')
    replace(subtitles, '        const candidates = buildCandidates(player.streamState?.subtitleTrack, subtitlesEnabled, settings.subtitlesLanguage);',
            '        const candidates = buildCandidates(player.streamState?.subtitleTrack, subtitlesEnabled, settings.subtitlesLanguage || CONSTANTS.DEFAULT_SUBTITLES_LANGUAGE);')
    replace(subtitles, '        player.streamState,\n        settings.subtitlesLanguage,',
            '        player.streamState,\n        tvSubtitleDefault.ready,\n        tvSubtitleDefault.enabled,\n        settings.subtitlesLanguage,')
    shutil.copyfile(ROOT / "client/TVRuntime.js", SOURCE / 'src/TVRuntime.js')
    shutil.copyfile(ROOT / 'client/TVAddonImport.js', SOURCE / 'src/App/TVAddonImport.js')
    shutil.copyfile(ROOT / 'client/TVAddonManager.js', SOURCE / 'src/App/TVAddonManager.js')
    search = SOURCE / 'src/components/NavBar/HorizontalNavBar/SearchBar/SearchBar.js'
    shutil.copyfile(ROOT / 'client/TVSearchKeyboard.js', search.parent / 'TVSearchKeyboard.js')
    replace(search, "const styles = require('./styles');", "const styles = require('./styles');\nconst TVSearchKeyboard = require('./TVSearchKeyboard');")
    replace(search, "    const searchInputRef = React.useRef(null);", "    const [keyboardOpen, setKeyboardOpen] = React.useState(false);\n    const searchInputRef = React.useRef(null);")
    if '        searchInputRef.current?.blur();' in search.read_text():
        replace(search, '        searchInputRef.current?.blur();', '        requestAnimationFrame(() => searchInputRef.current?.focus());')
    replace(search, '    const queryInputClear = React.useCallback(() => {', '''    const closeTVKeyboard = React.useCallback(() => {
        setKeyboardOpen(false);
        requestAnimationFrame(() => searchInputRef.current?.focus());
    }, []);
    const submitTVKeyboard = React.useCallback(() => {
        setSearchParams({search: currentQuery});
        closeHistory();
        closeTVKeyboard();
    }, [currentQuery, setSearchParams, closeHistory, closeTVKeyboard]);

    const queryInputClear = React.useCallback(() => {''')
    if '                        onFocus={() => setKeyboardOpen(true)}' in search.read_text():
        replace(search, '                        onFocus={() => setKeyboardOpen(true)}', '                        data-tv-search="true"')
    replace(search, '                        onClick={openHistory}', '                        onClick={() => {openHistory(); setKeyboardOpen(true);}}\n                        data-tv-search="true"')
    replace(search, '            searchInputRef.current.focus();', '            searchInputRef.current.focus();\n            setKeyboardOpen(true);')
    replace(search, '            {\n                currentQuery.length > 0 ?', '''            {keyboardOpen && <TVSearchKeyboard value={currentQuery} onChange={setCurrentQuery}
                onSubmit={submitTVKeyboard} onClose={closeTVKeyboard} />}
            {
                currentQuery.length > 0 ?''')
    app = SOURCE / 'src/App/App.js'
    replace(app, "const SearchParamsHandler = require('./SearchParamsHandler');", "const SearchParamsHandler = require('./SearchParamsHandler');\nconst TVAddonImport = require('./TVAddonImport');")
    replace(app, '                                    <SearchParamsHandler />', '                                    <SearchParamsHandler />\n                                    <TVAddonImport />')
    replace(app, "const TVAddonImport = require('./TVAddonImport');", "const TVAddonImport = require('./TVAddonImport');\nconst TVAddonManager = require('./TVAddonManager');")
    replace(app, '                                    <TVAddonImport />', '                                    <TVAddonImport />\n                                    <TVAddonManager />')
    replace(SOURCE / 'src/core/createTransport.ts', "return bridge.call(['analytics'], [event, location.hash]);", "return Promise.resolve(); // Owner build: do not send route/addon URLs as analytics.")
    replace(SOURCE / 'src/index.js', "const Bowser = require('bowser');", "require('./TVRuntime');\nconst Bowser = require('bowser');")
    replace(SOURCE / 'src/common/Platform/device.ts',
            "const supportsViewTransitions = !(os === 'linux' && bowser.getEngineName() === 'WebKit');",
            "const supportsViewTransitions = !/VIZIO|SmartCast|Conjure/i.test(userAgent) && !(os === 'linux' && bowser.getEngineName() === 'WebKit');")
    board = SOURCE / 'src/routes/Board/Board.js'
    replace(board, '            <EventModal />', '            {/* Seasonal promotion omitted in owner TV build. */}')
    mime_file = SOURCE / "node_modules/@stremio/stremio-video/src/HTMLVideo/getContentType.js"
    dependency_patch(mime_file.parent / 'hlsConfig.js', 'enableWorker: true,', 'enableWorker: false,', 'stremio-hls-worker.patch')
    dependency_patch(mime_file.parent / 'HTMLVideo.js',
        'hls.on(Hls.Events.ERROR, function(_event, data) {',
        '''hls.on(Hls.Events.ERROR, function(_event, data) {
                                    if (hls !== activeHls) return;
                                    var note = [data.type, data.details, data.error && data.error.message].filter(Boolean).join(': ').replace(/https?:\\/\\/\\S+/g, '[URL omitted]').slice(0, 700);
                                    fetch('/event', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({kind: 'stremio-hls-error', message: note})}).catch(function() {});''',
        'stremio-hls-errors.patch')
    original = mime_file.read_text()
    new = original.replace("return resp.headers.get('content-type');", "const mime = (resp.headers.get('content-type') || '').split(';')[0].trim().toLowerCase();\n            return ['audio/mpegurl', 'audio/x-mpegurl', 'application/x-mpegurl', 'application/mpegurl'].includes(mime) ? 'application/vnd.apple.mpegurl' : mime;")
    if new != original:
        # Replace the file inode: do not modify a pnpm store hardlink in place.
        temp = mime_file.with_suffix('.js.tv-new')
        temp.write_text(new)
        temp.replace(mime_file)
        diff = ''.join(difflib.unified_diff(original.splitlines(True), new.splitlines(True), fromfile='HTMLVideo/getContentType.js', tofile='HTMLVideo/getContentType.js'))
        (ROOT / 'research/reviews/stremio-mime-normalization.patch').write_text(diff)
    webpack = SOURCE / "webpack.config.js"
    replace(webpack, "'stremio-router': path.resolve(__dirname, 'src', 'router')", "'stremio-router': path.resolve(__dirname, 'src', 'router'),\n            'hls.js': path.resolve(__dirname, '../../web/vendor/hls.min.js')")
    replace(webpack, "SERVICE_WORKER_DISABLED: false,", "SERVICE_WORKER_DISABLED: true,")
    index = SOURCE / 'src/index.html'
    html = index.read_text()
    html = '\n'.join(line for line in html.splitlines() if 'cast_sender.js' not in line and 'appleid.auth.js' not in line) + '\n'
    index.write_text(html)
    print('Prepared local Stremio frontend: TV controls, HLS MIME normalization, tested HLS.js, no service worker.')


if __name__ == '__main__':
    main()
