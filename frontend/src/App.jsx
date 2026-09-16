import React, { useCallback, useEffect, useRef, useState } from 'react';
import * as cocoSsd from '@tensorflow-models/coco-ssd';
import '@tensorflow/tfjs';
import {
  Activity,
  AlertTriangle,
  BarChart3,
  Bell,
  BatteryCharging,
  Camera,
  CheckCircle2,
  ChevronRight,
  CircleHelp,
  Droplets,
  Gauge,
  Layers3,
  Map,
  MapPinned,
  Menu,
  Radio,
  ScanLine,
  Settings,
  ShieldCheck,
  Square,
  Trash2,
  UserRound,
  Waves,
  Wrench,
  X,
} from 'lucide-react';

const initialEvents = [
  { type: 'Blocked drain', area: '12th Main · Sector 4', time: 'just now', severity: 'high', icon: AlertTriangle },
  { type: 'Water level rising', area: 'Lakeview junction', time: '4 min ago', severity: 'medium', icon: Waves },
  { type: 'Route completed', area: 'Robot DB-04 · East loop', time: '12 min ago', severity: 'low', icon: CheckCircle2 },
];

const navItems = [
  { label: 'Vision hub', icon: ScanLine, active: true },
  { label: 'Live map', icon: Map },
  { label: 'Fleet health', icon: Gauge },
  { label: 'Analytics', icon: BarChart3 },
  { label: 'Alerts', icon: Bell },
  { label: 'Maintenance', icon: Wrench },
];

const systemModules = [
  { title: 'Live map', detail: 'GPS robot locations with green, amber and red status markers.', icon: MapPinned, tone: 'teal' },
  { title: 'Robot status', detail: 'Cleaning, idle, charging, fault and offline states at a glance.', icon: Radio, tone: 'blue' },
  { title: 'Emergency alerts', detail: 'Blockage, overflow, motor fault and communication-loss signals.', icon: Bell, tone: 'coral' },
  { title: 'Battery + solar', detail: 'Charge level, solar input and low-battery warnings.', icon: BatteryCharging, tone: 'amber' },
  { title: 'Waste bag status', detail: 'Fill percentage, weight, pickup request and full-bag alerts.', icon: Trash2, tone: 'amber' },
  { title: 'Drain condition', detail: 'Water level, flow and blockage severity from fused sensors.', icon: Waves, tone: 'blue' },
  { title: 'AI waste detection', detail: 'Leaves, paper, plastic, bottles and debris with confidence.', icon: ScanLine, tone: 'teal' },
  { title: 'Robot health', detail: 'Motor, wing, conveyor, camera, sensor and comms health.', icon: ShieldCheck, tone: 'teal' },
  { title: 'Reports + history', detail: 'Cleaning records, blockage events, faults and bag replacements.', icon: Layers3, tone: 'blue' },
  { title: 'Municipality action', detail: 'Assign a technician, request pickup or resolve an incident.', icon: Wrench, tone: 'coral' },
  { title: 'Safety mode', detail: 'Fold wings and park automatically when water conditions are unsafe.', icon: Square, tone: 'coral' },
  { title: 'Public reports', detail: 'Location, photo, problem type and description from residents.', icon: UserRound, tone: 'amber' },
];

const sectionModules = {
  'Vision hub': systemModules,
  'Live map': systemModules.filter(({ title }) => ['Live map', 'Robot status', 'Drain condition'].includes(title)),
  'Fleet health': systemModules.filter(({ title }) => ['Robot status', 'Battery + solar', 'Robot health', 'Safety mode'].includes(title)),
  Analytics: systemModules.filter(({ title }) => ['Waste bag status', 'AI waste detection', 'Reports + history'].includes(title)),
  Alerts: systemModules.filter(({ title }) => ['Emergency alerts', 'Drain condition', 'Public reports'].includes(title)),
  Maintenance: systemModules.filter(({ title }) => ['Robot health', 'Municipality action', 'Waste bag status'].includes(title)),
};

const sectionDescriptions = {
  'Vision hub': 'One clear view of every drain, robot, and risk in your district.',
  'Live map': 'Track robot positions, drain zones, and condition severity in real time.',
  'Fleet health': 'See power, sensors, communication, wings, and collection hardware at a glance.',
  Analytics: 'Turn detection events and collected waste into decisions for your next route.',
  Alerts: 'Prioritize incidents by severity, location, sensor evidence, and response window.',
  Maintenance: 'Move from fault detection to technician assignment and return-to-service.',
};

const detectedWasteLabels = {
  bottle: 'PLASTIC DETECTED · bottle',
  cup: 'PLASTIC DETECTED · cup',
  bowl: 'PLASTIC DETECTED · container',
  frisbee: 'PLASTIC DETECTED · disc',
  backpack: 'PLASTIC DETECTED · bag',
  handbag: 'PLASTIC DETECTED · bag',
  suitcase: 'PLASTIC DETECTED · case',
};

const plasticWasteClasses = Object.keys(detectedWasteLabels);

function App() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const imageInputRef = useRef(null);
  const streamRef = useRef(null);
  const previousFrameRef = useRef(null);
  const animationRef = useRef(null);
  const [cameraOn, setCameraOn] = useState(false);
  const [demoMode, setDemoMode] = useState(true);
  const [motionScore, setMotionScore] = useState(18);
  const [detections, setDetections] = useState(3);
  const [events, setEvents] = useState(initialEvents);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [activeSection, setActiveSection] = useState('Vision hub');
  const [notice, setNotice] = useState('Edge vision ready');
  const [detector, setDetector] = useState(null);
  const [modelStatus, setModelStatus] = useState('Loading AI model');
  const [detectionsFound, setDetectionsFound] = useState([]);
  const visibleModules = sectionModules[activeSection] || systemModules;

  const loadDetector = useCallback(() => {
    setModelStatus('Loading AI model');
    cocoSsd.load().then((model) => {
      setDetector(model);
      setModelStatus('AI model ready');
    }).catch(() => {
      setModelStatus('AI model unavailable · retry');
    });
  }, []);

  const analyzePhoto = useCallback((event) => {
    const file = event.target.files?.[0];
    if (!file || !detector) {
      setNotice('AI model is still loading');
      return;
    }
    const image = new Image();
    const imageUrl = URL.createObjectURL(file);
    image.onload = async () => {
      try {
        const predictions = await detector.detect(image);
        const relevant = predictions
          .filter(({ class: label, score: confidence }) => confidence >= 0.3 && plasticWasteClasses.includes(label))
          .map((prediction) => ({ ...prediction, displayLabel: detectedWasteLabels[prediction.class] }));
        setDetectionsFound(relevant.slice(0, 3));
        setNotice(relevant.length ? `${relevant[0].displayLabel} · ${Math.round(relevant[0].score * 100)}% confidence` : 'No plastic item found in photo');
      } catch {
        setNotice('Photo scan failed · try another image');
      } finally {
        URL.revokeObjectURL(imageUrl);
      }
    };
    image.src = imageUrl;
    event.target.value = '';
  }, [detector]);

  const stopCamera = useCallback(() => {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    if (videoRef.current) videoRef.current.srcObject = null;
    setCameraOn(false);
    setNotice('Camera paused');
  }, []);

  const startCamera = useCallback(async () => {
    if (!navigator.mediaDevices?.getUserMedia) {
      setNotice('Camera access is not supported in this browser');
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment', width: 1280, height: 720 }, audio: false });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      setDemoMode(false);
      setCameraOn(true);
      setNotice('Live camera connected');
    } catch {
      setNotice('Camera blocked · allow permission, then try again');
      setDemoMode(true);
    }
  }, []);

  useEffect(() => () => stopCamera(), [stopCamera]);

  useEffect(() => {
    const scan = () => {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      if (video && canvas && cameraOn && video.readyState >= 2) {
        const context = canvas.getContext('2d', { willReadFrequently: true });
        canvas.width = 160;
        canvas.height = 90;
        context.drawImage(video, 0, 0, 160, 90);
        const pixels = context.getImageData(0, 0, 160, 90).data;
        let difference = 0;
        if (previousFrameRef.current) {
          for (let index = 0; index < pixels.length; index += 16) difference += Math.abs(pixels[index] - previousFrameRef.current[index]);
        }
        previousFrameRef.current = pixels;
        const score = Math.min(99, Math.round(difference / 2700));
        setMotionScore(score);
        if (score > 36) {
          setDetections((value) => Math.min(9, value + 1));
          setNotice('Anomaly detected · reviewing frame');
        }
        if (detector && !scan.running) {
          scan.running = true;
          detector.detect(video).then((predictions) => {
            const relevant = predictions
              .filter(({ class: label, score: confidence }) => confidence >= 0.3 && plasticWasteClasses.includes(label))
              .map((prediction) => ({ ...prediction, displayLabel: detectedWasteLabels[prediction.class] || prediction.class }));
            setDetectionsFound(relevant.slice(0, 3));
            if (relevant.length) {
              const best = relevant[0];
              setNotice(`${best.displayLabel} detected · ${Math.round(best.score * 100)}% confidence`);
              setDetections((value) => Math.max(value, relevant.length));
            }
          }).catch(() => setNotice('AI scan unavailable · motion scan active')).finally(() => { scan.running = false; });
        }
      } else if (demoMode) {
        setMotionScore((value) => Math.max(10, Math.min(52, value + (Math.random() > 0.65 ? 4 : -2))));
      }
      animationRef.current = requestAnimationFrame(scan);
    };
    animationRef.current = requestAnimationFrame(scan);
    return () => cancelAnimationFrame(animationRef.current);
  }, [cameraOn, demoMode, detector]);

  useEffect(() => {
    loadDetector();
  }, [loadDetector]);

  const addIncident = () => {
    setEvents((current) => [{ type: 'Visual check logged', area: 'Camera 01 · North inlet', time: 'just now', severity: 'medium', icon: Radio }, ...current].slice(0, 4));
    setNotice('Incident logged to operations feed');
  };

  return (
    <div className="app-shell">
      <aside className={`sidebar ${sidebarOpen ? 'sidebar-open' : ''}`}>
        <div className="brand-row">
          <div className="brand-mark"><Droplets size={20} strokeWidth={2.5} /></div>
          <div><strong>drainbot</strong><span>VISION CONSOLE</span></div>
          <button className="icon-button close-menu" onClick={() => setSidebarOpen(false)} aria-label="Close menu"><X size={19} /></button>
        </div>
        <div className="workspace-switcher"><span className="status-dot" /> North district <ChevronRight size={15} /></div>
        <p className="nav-label">OPERATIONS</p>
        <nav>{navItems.map(({ label, icon: Icon }) => <button key={label} onClick={() => { setActiveSection(label); setSidebarOpen(false); }} className={`nav-item ${activeSection === label ? 'active' : ''}`}><Icon size={18} /><span>{label}</span>{activeSection === label && <span className="nav-pip" />}</button>)}</nav>
        <div className="sidebar-spacer" />
        <div className="health-card"><div className="health-title"><ShieldCheck size={17} /> System health <span>98%</span></div><div className="health-bar"><i /></div><small>All detection services operational</small></div>
        <button className="nav-item"><Settings size={18} /><span>Settings</span></button>
        <div className="profile-row"><div className="avatar">J</div><div><strong>Jai</strong><small>Field supervisor</small></div><CircleHelp size={17} /></div>
      </aside>
      {sidebarOpen && <button className="sidebar-scrim" onClick={() => setSidebarOpen(false)} aria-label="Close navigation" />}

      <main className="main-content">
        <header className="topbar"><button className="icon-button menu-button" onClick={() => setSidebarOpen(true)} aria-label="Open menu"><Menu size={22} /></button><div className="breadcrumb"><span>Operations</span><ChevronRight size={15} /><strong>Vision hub</strong></div><div className="top-actions"><span className="live-chip"><span className="pulse" /> Live network</span><button className="icon-button" aria-label="Notifications"><Bell size={19} /><b>3</b></button><div className="top-avatar">J</div></div></header>
        <section className="page-heading"><div><p className="eyebrow">MONITORING CENTER <span>•</span> 13 SEP 2026</p><h1>{activeSection === 'Vision hub' ? 'Hi Jai' : activeSection}</h1><p className="lede">{sectionDescriptions[activeSection]}</p></div><button className="outline-button" onClick={addIncident}><Bell size={16} /> Log incident</button></section>

        <section className="metric-grid">
          <Metric label="Active cameras" value="08" detail="2 scanning now" icon={Camera} tone="teal" />
          <Metric label="Detections today" value={String(detections).padStart(2, '0')} detail="+18% vs yesterday" icon={ScanLine} tone="amber" />
          <Metric label="Open incidents" value="04" detail="1 needs attention" icon={AlertTriangle} tone="coral" />
          <Metric label="Network uptime" value="99.8%" detail="Last 30 days" icon={Activity} tone="blue" />
        </section>

        <section className="content-grid">
          <div className="camera-panel panel">
            <div className="panel-heading"><div><div className="panel-kicker"><span className="live-dot" /> LIVE FEED 01</div><h2>North inlet camera</h2></div><div className="feed-actions"><span className={`mode-label ${demoMode ? 'demo-label' : ''}`}>{demoMode ? 'Demo feed' : 'Camera online'}</span><button className="icon-button" aria-label="Camera settings"><Settings size={17} /></button></div></div>
            <div className="camera-stage">
              <video ref={videoRef} muted playsInline className={cameraOn ? 'video-visible' : ''} />
              <div className={`demo-scene ${cameraOn ? 'camera-active' : ''}`}><div className="scene-grid" /><div className="drain-ring" /><div className="water-line" /><div className="demo-label-card"><span>DEMO ENVIRONMENT</span><strong>North inlet · Sector 04</strong></div></div>
              <div className="scan-line" /><div className="corner top-left" /><div className="corner top-right" /><div className="corner bottom-left" /><div className="corner bottom-right" />
              {!cameraOn && <><div className="detection-box box-one"><span>DEMO BLOCKAGE · 87%</span></div><div className="detection-box box-two"><span>DEMO WATER LEVEL · 74%</span></div></>}
              {detectionsFound.map(({ class: label, displayLabel, score, bbox }, index) => <div className={`detection-box model-box model-box-${index}`} key={`${label}-${index}`} style={{ left: `${(bbox[0] / 640) * 100}%`, top: `${(bbox[1] / 480) * 100}%`, width: `${(bbox[2] / 640) * 100}%`, height: `${(bbox[3] / 480) * 100}%` }}><span>{displayLabel.toUpperCase()} · {Math.round(score * 100)}%</span></div>)}
              <div className="camera-meta"><span><Radio size={14} /> 1080p · 24 FPS</span><span><span className="green-dot" /> {notice}</span></div>
            </div>
            <div className="camera-footer"><div className="camera-controls"><button className={`primary-button ${cameraOn ? 'stop' : ''}`} onClick={cameraOn ? stopCamera : startCamera}>{cameraOn ? <Square size={16} /> : <Camera size={17} />}{cameraOn ? 'Stop camera' : 'Use my camera'}</button><button className="secondary-button" onClick={() => { setDemoMode(true); stopCamera(); }}>Demo mode</button><button className="secondary-button" onClick={() => imageInputRef.current?.click()}>Scan photo</button><input ref={imageInputRef} type="file" accept="image/*" onChange={analyzePhoto} hidden /></div><div className="scan-status"><span>{modelStatus}</span>{modelStatus.includes('retry') && <button className="text-button" onClick={loadDetector}>Retry</button>}<strong>{detectionsFound.length ? `${detectionsFound.length} found` : `${Math.max(74, 96 - motionScore)}%`}</strong><div className="confidence-bar"><i style={{ width: `${detectionsFound.length ? 100 : Math.max(74, 96 - motionScore)}%` }} /></div></div></div>
          </div>

          <div className="side-column"><div className="panel risk-panel"><div className="panel-heading compact"><div><div className="panel-kicker">RISK PULSE</div><h2>Live conditions</h2></div><button className="more-button">•••</button></div><div className="risk-reading"><div className="gauge"><div className="gauge-value">74<span>%</span></div><small>water level</small></div><div className="risk-copy"><span className="warning-badge">Elevated</span><strong>Prepare response crew</strong><p>Water is rising near the north inlet. Dispatch window is under 18 minutes.</p></div></div><div className="mini-stats"><div><span>Flow rate</span><strong>42.8 <small>L/min</small></strong></div><div><span>Last cleared</span><strong>2h 14m <small>ago</small></strong></div></div></div><div className="panel events-panel"><div className="panel-heading compact"><div><div className="panel-kicker">ACTIVITY STREAM</div><h2>Recent signals</h2></div><button className="text-button">View all</button></div><div className="events-list">{events.map(({ type, area, time, severity, icon: Icon }, index) => <div className="event-row" key={`${type}-${index}`}><div className={`event-icon ${severity}`}><Icon size={16} /></div><div className="event-copy"><strong>{type}</strong><span>{area}</span></div><time>{time}</time></div>)}</div></div></div>
        </section>
        <section className="modules-section"><div className="section-heading"><div><p className="eyebrow">DRAINBOT OS <span>•</span> {activeSection.toUpperCase()}</p><h2>{activeSection === 'Vision hub' ? 'Everything your district needs' : `${activeSection} workspace`}</h2></div><span className="module-count">{visibleModules.length} modules online</span></div><div className="module-grid">{visibleModules.map(({ title, detail, icon: Icon, tone }) => <button className="module-card" key={title} onClick={() => setNotice(`${title} module selected`)}><span className={`module-icon ${tone}`}><Icon size={17} /></span><span className="module-copy"><strong>{title}</strong><small>{detail}</small></span><ChevronRight size={16} className="module-arrow" /></button>)}</div></section>
        <footer className="footer-note"><span><span className="green-dot" /> Edge detection active</span><span>Last sync 12 seconds ago</span><span>DrainBot OS v2.4.1</span></footer>
      </main>
      <canvas ref={canvasRef} className="hidden-canvas" />
    </div>
  );
}

function Metric({ label, value, detail, icon: Icon, tone }) {
  return <div className="metric-card"><div className={`metric-icon ${tone}`}><Icon size={19} /></div><div className="metric-text"><span>{label}</span><strong>{value}</strong><small>{detail}</small></div></div>;
}

export default App;
