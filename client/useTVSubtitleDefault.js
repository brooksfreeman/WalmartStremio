const React = require('react');

// Re-read for every stream, including next episodes. Never reset a viewer's
// manual caption choice while the current stream is playing.
let lastDefault = true;

function useTVSubtitleDefault(stream) {
    const [result, setResult] = React.useState(null);
    React.useEffect(() => {
        if (stream === null) return;
        let active = true;
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 2000);
        (async () => {
            let enabled = lastDefault;
            try {
                const response = await fetch('/playback-preferences', {
                    cache: 'no-store', signal: controller.signal,
                });
                if (!response.ok) throw new Error('Preferences unavailable');
                const value = await response.json();
                if (typeof value.subtitles_default_on !== 'boolean') throw new Error('Invalid preference');
                enabled = value.subtitles_default_on;
            } catch (_) {
                // A temporary host failure must not prevent playback.
            } finally {
                clearTimeout(timeout);
            }
            if (active) {
                lastDefault = enabled;
                setResult({stream, enabled});
            }
        })();
        return () => {
            active = false;
            clearTimeout(timeout);
            controller.abort();
        };
    }, [stream]);
    return {ready: stream !== null && result?.stream === stream, enabled: result?.enabled ?? lastDefault};
}

module.exports = useTVSubtitleDefault;
