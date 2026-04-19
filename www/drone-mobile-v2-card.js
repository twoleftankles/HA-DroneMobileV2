/**
 * DroneMobile V2 — Custom Lovelace Card v1.2.0
 * - Visual editor with per-item selection
 * - Mini map showing vehicle location
 * - HA theme-aware styling
 */

const CARD_VERSION = '1.6.1';

const VEHICLE_ICONS = [
  { value: 'mdi:car-connected',   label: 'Connected Car (default)' },
  { value: 'mdi:car',             label: 'Car' },
  { value: 'mdi:car-sports',      label: 'Sports Car' },
  { value: 'mdi:car-estate',      label: 'Estate / Wagon' },
  { value: 'mdi:car-pickup',      label: 'Pickup Truck' },
  { value: 'mdi:truck',           label: 'Truck' },
  { value: 'mdi:truck-pickup',    label: 'Truck (Pickup)' },
  { value: 'mdi:van-utility',     label: 'Van / Utility' },
  { value: 'mdi:bus',             label: 'Bus' },
  { value: 'mdi:motorcycle',      label: 'Motorcycle' },
  { value: 'mdi:rv-truck',        label: 'RV / Motorhome' },
  { value: 'mdi:tractor',         label: 'Tractor' },
  { value: 'mdi:ambulance',       label: 'Ambulance' },
  { value: 'mdi:police-badge',    label: 'Police' },
  { value: 'mdi:fire-truck',      label: 'Fire Truck' },
];

// All configurable items grouped by section
const CARD_ITEMS = {
  status: {
    label: 'Status',
    items: [
      { key: 'engine',   label: 'Engine Status',  icon: 'mdi:engine' },
      { key: 'alarm',    label: 'Alarm',           icon: 'mdi:shield-car' },
      { key: 'ignition', label: 'Ignition',        icon: 'mdi:key-variant' },
      { key: 'remote',   label: 'Remote Start',    icon: 'mdi:car-key' },
      { key: 'panic',    label: 'Panic Status',    icon: 'mdi:alarm-light' },
      { key: 'towing',   label: 'Towing',          icon: 'mdi:tow-truck' },
    ],
  },
  telemetry: {
    label: 'Telemetry',
    items: [
      { key: 'speed',    label: 'Speed',       icon: 'mdi:speedometer' },
      { key: 'odometer', label: 'Odometer',    icon: 'mdi:counter' },
      { key: 'temp',     label: 'Temperature', icon: 'mdi:thermometer' },
      { key: 'heading',  label: 'Heading',     icon: 'mdi:compass' },
    ],
  },
  battery: {
    label: 'Battery',
    items: [
      { key: 'main_battery',   label: 'Main Battery',   icon: 'mdi:car-battery' },
      { key: 'backup_battery', label: 'Backup Battery', icon: 'mdi:battery-heart' },
    ],
  },
  doors: {
    label: 'Doors & Access',
    items: [
      { key: 'door',  label: 'Door',  icon: 'mdi:car-door' },
      { key: 'trunk', label: 'Trunk', icon: 'mdi:car-back' },
      { key: 'hood',  label: 'Hood',  icon: 'mdi:car' },
    ],
  },
  controls: {
    label: 'Controls',
    items: [
      { key: 'lock',         label: 'Lock / Unlock',  icon: 'mdi:lock' },
      { key: 'remote_start', label: 'Remote Start',   icon: 'mdi:play-circle' },
      { key: 'remote_stop',  label: 'Remote Stop',    icon: 'mdi:stop-circle' },
      { key: 'trunk_btn',    label: 'Trunk Release',  icon: 'mdi:car-back' },
      { key: 'aux1',         label: 'Aux 1',          icon: 'mdi:numeric-1-circle' },
      { key: 'aux2',         label: 'Aux 2',          icon: 'mdi:numeric-2-circle' },
      { key: 'panic_btn',    label: 'Panic Button',   icon: 'mdi:alarm-light' },
    ],
  },
  settings: {
    label: 'Controller Settings',
    items: [
      { key: 'valet_mode',        label: 'Valet Mode',       icon: 'mdi:car-key' },
      { key: 'siren',             label: 'Siren',            icon: 'mdi:bullhorn' },
      { key: 'shock_sensor',      label: 'Shock Sensor',     icon: 'mdi:vibrate' },
      { key: 'passive_arming',    label: 'Passive Arming',   icon: 'mdi:lock-clock' },
      { key: 'auto_door_lock',    label: 'Auto Door Lock',   icon: 'mdi:car-door-lock' },
      { key: 'drive_lock',        label: 'Drive Lock',       icon: 'mdi:lock-open-variant' },
      { key: 'timer_start',       label: 'Timer Start',      icon: 'mdi:timer-outline' },
      { key: 'turbo_timer_start', label: 'Turbo Timer',      icon: 'mdi:timer-cog-outline' },
    ],
  },
  diagnostics: {
    label: 'Diagnostics',
    items: [
      { key: 'maintenance',  label: 'Maintenance Due',  icon: 'mdi:wrench-clock' },
      { key: 'low_battery',  label: 'Low Battery',      icon: 'mdi:battery-alert' },
      { key: 'firmware',     label: 'Firmware Version', icon: 'mdi:chip' },
      { key: 'model',        label: 'Controller Model', icon: 'mdi:car-cog' },
      { key: 'carrier',      label: 'Carrier',          icon: 'mdi:sim' },
      { key: 'signal',       label: 'Signal Strength',  icon: 'mdi:signal' },
      { key: 'last_cmd',     label: 'Last Command',     icon: 'mdi:remote' },
      { key: 'api_errors',   label: 'API Errors',       icon: 'mdi:alert-circle' },
    ],
  },
};

function itemDefault(sectionKey, itemKey) {
  const defaults = {
    diagnostics: false,
    settings_turbo_timer_start: false,
    settings_timer_start: false,
    controls_aux1: false,
    controls_aux2: false,
  };
  return defaults[`${sectionKey}_${itemKey}`] ?? (sectionKey !== 'diagnostics');
}

function isItemOn(config, sectionKey, itemKey) {
  const cfgKey = `${sectionKey}_${itemKey}`;
  return cfgKey in config ? config[cfgKey] : itemDefault(sectionKey, itemKey);
}


// ── Visual Editor ─────────────────────────────────────────────────────────────

class DroneMobileV2CardEditor extends HTMLElement {
  constructor() {
    super();
    this._config = {};
    this._detectedVehicles = null;
  }

  setConfig(config) {
    this._config = { ...config };
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    const vehicles = this._detectVehicles();
    const key = vehicles.join(',');
    if (key !== (this._detectedVehicles || []).join(',')) {
      this._detectedVehicles = vehicles;
      this._render();
    }
  }

  _detectVehicles() {
    if (!this._hass) return [];
    return Object.keys(this._hass.states)
      .filter(id => id.startsWith('device_tracker.') && id.endsWith('_location'))
      .map(id => id.slice('device_tracker.'.length, -'_location'.length))
      .sort();
  }

  _buildVehicleInput() {
    const vehicles = this._detectedVehicles || [];
    if (vehicles.length === 0) {
      return `
        <input class="field-input" id="inp-vehicle" type="text" placeholder="e.g. f_250" value="${this._config.vehicle || ''}">
        <div class="field-hint">Slug in your entity IDs, e.g. sensor.<strong>f_250</strong>_engine_status</div>`;
    }
    const current = this._config.vehicle || vehicles[0];
    return `
      <select class="field-input" id="inp-vehicle">
        ${vehicles.map(v => `<option value="${v}" ${current === v ? 'selected' : ''}>${v.replace(/_/g, ' ')}</option>`).join('')}
      </select>
      <div class="field-hint">Auto-detected from your DroneMobile V2 integration</div>`;
  }

  _render() {
    this.innerHTML = `
      <style>
        .editor { display: flex; flex-direction: column; gap: 16px; padding: 4px 0; }
        .field-label { font-size: 0.78em; color: var(--secondary-text-color); font-weight: 500; margin-bottom: 4px; }
        .field-input {
          width: 100%; box-sizing: border-box; padding: 8px 10px;
          border: 1px solid var(--divider-color); border-radius: 6px;
          background: var(--card-background-color); color: var(--primary-text-color);
          font-size: 0.95em; font-family: inherit;
        }
        .field-input:focus { outline: none; border-color: var(--primary-color); }
        .field-hint { font-size: 0.7em; color: var(--secondary-text-color); margin-top: 3px; }
        .section-block { border: 1px solid var(--divider-color); border-radius: 10px; overflow: hidden; }
        .section-header {
          display: flex; align-items: center; justify-content: space-between;
          padding: 10px 14px; background: var(--secondary-background-color);
          cursor: pointer; user-select: none;
        }
        .section-header-label { font-size: 0.85em; font-weight: 600; }
        .section-body { padding: 8px 14px; display: flex; flex-direction: column; gap: 6px; }
        .item-row {
          display: flex; align-items: center; justify-content: space-between;
          padding: 4px 0;
        }
        .item-label { font-size: 0.85em; }
        ha-switch { flex-shrink: 0; }
        .map-toggle-row {
          display: flex; align-items: center; justify-content: space-between;
          padding: 10px 14px; border: 1px solid var(--divider-color);
          border-radius: 10px; background: var(--secondary-background-color);
        }
        .map-toggle-label { font-size: 0.85em; font-weight: 600; }
      </style>
      <div class="editor">
        <div>
          <div class="field-label">Vehicle *</div>
          ${this._buildVehicleInput()}
        </div>
        <div>
          <div class="field-label">Display Name</div>
          <input class="field-input" id="inp-name" type="text" placeholder="e.g. F-250 Super Duty" value="${this._config.name || ''}">
        </div>

        <div class="map-toggle-row">
          <span class="map-toggle-label">Show Mini Map</span>
          <ha-switch id="sw-show_map" ${this._get('show_map', true) ? 'checked' : ''}></ha-switch>
        </div>
        <div>
          <div class="field-label">Map Zoom Level</div>
          <input class="field-input" id="inp-map_zoom" type="number" min="1" max="20" step="1"
            value="${this._get('map_zoom', 14)}" style="width:80px;">
          <div class="field-hint">1 = world, 14 = street (default), 18 = building</div>
        </div>
        <div>
          <div class="field-label">Map Vehicle Icon</div>
          <select class="field-input" id="inp-vehicle_icon">
            ${VEHICLE_ICONS.map(i => `<option value="${i.value}" ${this._get('vehicle_icon', 'mdi:car-connected') === i.value ? 'selected' : ''}>${i.label}</option>`).join('')}
          </select>
        </div>

        ${Object.entries(CARD_ITEMS).map(([sKey, section]) => `
          <div class="section-block">
            <div class="section-header">
              <span class="section-header-label">${section.label}</span>
            </div>
            <div class="section-body">
              ${section.items.map(item => `
                <div class="item-row">
                  <span class="item-label">${item.label}</span>
                  <ha-switch data-section="${sKey}" data-item="${item.key}"
                    ${isItemOn(this._config, sKey, item.key) ? 'checked' : ''}></ha-switch>
                </div>
              `).join('')}
            </div>
          </div>
        `).join('')}
      </div>
    `;

    this.querySelector('#inp-vehicle').addEventListener('change', e => this._set('vehicle', e.target.value.trim()));
    this.querySelector('#inp-name').addEventListener('change',    e => this._set('name', e.target.value.trim()));
    this.querySelector('#sw-show_map').addEventListener('change', e => this._set('show_map', e.target.checked));
    this.querySelector('#inp-map_zoom').addEventListener('change', e => this._set('map_zoom', parseInt(e.target.value, 10) || 14));
    this.querySelector('#inp-vehicle_icon').addEventListener('change', e => this._set('vehicle_icon', e.target.value));

    // If no vehicle is saved yet but one was auto-selected in the dropdown, persist it now
    const detected = this._detectedVehicles || [];
    if (!this._config.vehicle && detected.length > 0) {
      this._set('vehicle', detected[0]);
    }

    this.querySelectorAll('ha-switch[data-section]').forEach(sw => {
      sw.addEventListener('change', e => {
        const cfgKey = `${e.target.dataset.section}_${e.target.dataset.item}`;
        this._set(cfgKey, e.target.checked);
      });
    });
  }

  _get(key, def) {
    return key in this._config ? this._config[key] : def;
  }

  _set(key, value) {
    this._config = { ...this._config, [key]: value };
    this.dispatchEvent(new CustomEvent('config-changed', {
      detail: { config: this._config },
      bubbles: true,
      composed: true,
    }));
  }
}

customElements.define('drone-mobile-v2-card-editor', DroneMobileV2CardEditor);


// ── Main Card ─────────────────────────────────────────────────────────────────

class DroneMobileV2Card extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._hass = null;
    this._config = null;
    this._rendered = false;
  }

  static getConfigElement() {
    return document.createElement('drone-mobile-v2-card-editor');
  }

  static getStubConfig() {
    return { vehicle: '', name: 'My Vehicle', show_map: true, map_zoom: 14, vehicle_icon: 'mdi:car-connected' };
  }

  setConfig(config) {
    const changed = JSON.stringify(config) !== JSON.stringify(this._config);
    this._config = config;
    if (changed) { this._rendered = false; this._render(); }
  }

  set hass(hass) {
    this._hass = hass;
    if (!this._rendered) this._render();
    this._update();
  }

  // ── Config helpers ─────────────────────────────────────────────────────────

  _on(sectionKey, itemKey) {
    return isItemOn(this._config, sectionKey, itemKey);
  }

  _eid(domain, key) { return `${domain}.${this._config.vehicle}_${key}`; }
  _e(domain, key)   { return this._hass?.states[this._eid(domain, key)]; }
  _state(domain, key) { return this._e(domain, key)?.state ?? 'unavailable'; }
  _attr(domain, key, attr) { return this._e(domain, key)?.attributes?.[attr]; }
  _svc(domain, service, eid) { this._hass.callService(domain, service, { entity_id: eid }); }
  _btn(key) { this._svc('button', 'press', this._eid('button', key)); }

  // ── Build HTML shell ───────────────────────────────────────────────────────

  _render() {
    if (!this._config) return;
    this._rendered = true;

    if (!this._config.vehicle) {
      this.shadowRoot.innerHTML = `
        <ha-card style="padding:20px;display:flex;align-items:center;gap:12px;color:var(--secondary-text-color)">
          <ha-icon icon="mdi:car-connected" style="--mdc-icon-size:28px;color:var(--primary-color)"></ha-icon>
          <span>Select a vehicle in the card editor to get started.</span>
        </ha-card>`;
      return;
    }

    const on = (s, i) => this._on(s, i);
    const showMap = this._config.show_map !== false;

    // Which sections have any item enabled?
    const hasStatus  = ['engine','alarm','ignition','remote','panic','towing'].some(k => on('status', k));
    const hasTele    = ['speed','odometer','temp','heading'].some(k => on('telemetry', k));
    const hasBattery = on('battery','main_battery') || on('battery','backup_battery');
    const hasDoors   = on('doors','door') || on('doors','trunk') || on('doors','hood');
    const hasLock    = on('controls','lock');
    const hasCtrl    = ['remote_start','remote_stop','trunk_btn','aux1','aux2','panic_btn'].some(k => on('controls', k));
    const hasSettings = CARD_ITEMS.settings.items.some(i => on('settings', i.key));
    const hasDiag    = CARD_ITEMS.diagnostics.items.some(i => on('diagnostics', i.key));

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }
        ha-card {
          padding: 0;
          overflow: hidden;
          border-radius: var(--ha-card-border-radius, 14px);
          background: var(--ha-card-background, var(--card-background-color));
          color: var(--primary-text-color);
        }

        /* Header */
        .header {
          display: flex; align-items: center; justify-content: space-between;
          padding: 16px 18px 14px;
          background: var(--ha-card-background, var(--card-background-color));
          border-bottom: 1px solid var(--divider-color);
        }
        .header-left { display: flex; align-items: center; gap: 12px; }
        .header-icon-wrap {
          display: flex; align-items: center; justify-content: center;
          width: 40px; height: 40px; border-radius: 10px;
          background: var(--secondary-background-color);
          border: 1px solid var(--divider-color);
          flex-shrink: 0;
        }
        .header-icon { --mdc-icon-size: 22px; color: var(--primary-color); }
        .vehicle-name { font-size: 1.05em; font-weight: 700; color: var(--primary-text-color); }
        .vehicle-sub  { font-size: 0.7em; color: var(--secondary-text-color); margin-top: 2px; }
        .last-update  { font-size: 0.68em; color: var(--secondary-text-color); text-align: right; line-height: 1.5; }

        /* Mini map iframe wrapper */
        .map-wrap {
          width: 100%; height: 180px; overflow: hidden; position: relative;
          background: var(--secondary-background-color);
        }
        .map-wrap ha-map {
          position: absolute; inset: 0; width: 100%; height: 100%;
        }
        .map-placeholder {
          display: flex; align-items: center; justify-content: center;
          height: 100%; color: var(--secondary-text-color); font-size: 0.85em; gap: 8px;
        }

        /* Section */
        .section { padding: 12px 16px; }
        .section-title {
          font-size: 0.67em; font-weight: 700; letter-spacing: 0.09em;
          text-transform: uppercase; color: var(--secondary-text-color); margin-bottom: 8px;
        }
        .divider { height: 1px; background: var(--divider-color); }

        /* Status chips */
        .chip-grid { display: grid; gap: 8px; }
        .chip-grid-3 { grid-template-columns: repeat(3, 1fr); }
        .chip-grid-2 { grid-template-columns: repeat(2, 1fr); }
        .chip-grid-1 { grid-template-columns: 1fr; }
        .status-chip {
          display: flex; flex-direction: column; align-items: center; gap: 3px;
          padding: 8px 4px; border-radius: 10px;
          background: var(--secondary-background-color);
          min-width: 0;
        }
        .status-chip ha-icon { --mdc-icon-size: 18px; }
        .chip-label { font-size: 0.6em; color: var(--secondary-text-color); text-align: center; }
        .chip-value { font-size: 0.75em; font-weight: 600; text-align: center; }

        /* Telemetry */
        .tele-row { display: flex; justify-content: space-around; padding: 12px 8px; flex-wrap: wrap; gap: 8px; }
        .tele-item { display: flex; flex-direction: column; align-items: center; gap: 2px; min-width: 60px; }
        .tele-value { font-size: 1em; font-weight: 700; }
        .tele-label { font-size: 0.62em; color: var(--secondary-text-color); text-transform: uppercase; letter-spacing: 0.05em; }

        /* Battery */
        .battery-card {
          padding: 12px 14px; border-radius: 10px;
          background: var(--secondary-background-color); margin-bottom: 6px;
        }
        .battery-card:last-child { margin-bottom: 0; }
        .battery-header { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
        .battery-header ha-icon { --mdc-icon-size: 22px; flex-shrink: 0; }
        .battery-meta { flex: 1; }
        .battery-lbl    { font-size: 0.68em; color: var(--secondary-text-color); text-transform: uppercase; letter-spacing: 0.05em; }
        .battery-status { font-size: 0.78em; font-weight: 600; margin-top: 1px; }
        .battery-voltage { font-size: 1.2em; font-weight: 700; font-variant-numeric: tabular-nums; }
        .bar-wrap { height: 6px; background: var(--divider-color); border-radius: 3px; overflow: hidden; }
        .bar { height: 100%; border-radius: 3px; transition: width 0.5s ease, background 0.5s ease; }

        /* Doors */
        .door-row { display: grid; gap: 8px; }
        .door-row-3 { grid-template-columns: repeat(3, 1fr); }
        .door-row-2 { grid-template-columns: repeat(2, 1fr); }
        .door-chip {
          display: flex; align-items: center; gap: 6px; padding: 8px 10px;
          border-radius: 8px; background: var(--secondary-background-color);
        }
        .door-chip ha-icon { --mdc-icon-size: 18px; flex-shrink: 0; }
        .door-name  { font-size: 0.68em; color: var(--secondary-text-color); }
        .door-state { font-size: 0.82em; font-weight: 600; }

        /* Lock */
        .lock-row { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
        .lock-btn {
          display: flex; align-items: center; justify-content: center; gap: 8px;
          padding: 11px; border-radius: 10px; border: none; cursor: pointer;
          font-size: 0.88em; font-weight: 600; font-family: inherit;
          transition: filter 0.15s, transform 0.1s;
        }
        .lock-btn:active { transform: scale(0.97); filter: brightness(0.9); }
        .lock-btn ha-icon { --mdc-icon-size: 18px; }
        .btn-lock   { background: var(--success-color, #4CAF50); color: #fff; }
        .btn-unlock { background: var(--error-color,   #F44336); color: #fff; }

        /* Controls */
        .ctrl-grid { display: grid; gap: 8px; }
        .ctrl-grid-3 { grid-template-columns: repeat(3, 1fr); }
        .ctrl-grid-2 { grid-template-columns: repeat(2, 1fr); }
        .ctrl-grid-1 { grid-template-columns: 1fr; }
        .ctrl-btn {
          display: flex; flex-direction: column; align-items: center; gap: 5px;
          padding: 10px 4px; border-radius: 10px;
          background: var(--secondary-background-color);
          border: none; cursor: pointer; color: var(--primary-text-color);
          font-family: inherit; transition: filter 0.15s, transform 0.1s;
        }
        .ctrl-btn:active { transform: scale(0.95); filter: brightness(0.9); }
        .ctrl-btn ha-icon { --mdc-icon-size: 20px; }
        .ctrl-btn span    { font-size: 0.65em; color: var(--secondary-text-color); }

        /* Settings */
        .switch-list { display: flex; flex-direction: column; gap: 5px; }
        .switch-row {
          display: flex; align-items: center; justify-content: space-between;
          padding: 8px 12px; border-radius: 8px;
          background: var(--secondary-background-color);
        }
        .switch-label { font-size: 0.84em; }

        /* Diagnostics */
        .diag-list { display: flex; flex-direction: column; gap: 4px; }
        .diag-row {
          display: flex; justify-content: space-between; align-items: center;
          padding: 6px 12px; border-radius: 6px;
          background: var(--secondary-background-color);
        }
        .diag-key   { font-size: 0.76em; color: var(--secondary-text-color); }
        .diag-value { font-size: 0.82em; font-weight: 600; }
      </style>

      <ha-card>

        <!-- Header -->
        <div class="header">
          <div class="header-left">
            <div class="header-icon-wrap">
              <ha-icon class="header-icon" icon="mdi:car-connected"></ha-icon>
            </div>
            <div>
              <div class="vehicle-name">${this._config.name || this._config.vehicle}</div>
              <div class="vehicle-sub">DroneMobile V2</div>
            </div>
          </div>
          <div class="last-update" id="last-update">Updating…</div>
        </div>

        <!-- Mini Map -->
        ${showMap ? `<div class="map-wrap" id="map-wrap"><div class="map-placeholder"><ha-icon icon="mdi:map-marker" style="--mdc-icon-size:18px"></ha-icon><span>Loading map…</span></div></div><div class="divider"></div>` : ''}

        <!-- Status -->
        ${hasStatus ? `
        <div class="section">
          <div class="section-title">Status</div>
          <div class="chip-grid chip-grid-3" id="chip-grid"></div>
        </div>
        <div class="divider"></div>` : ''}

        <!-- Telemetry -->
        ${hasTele ? `<div class="tele-row" id="tele-row"></div><div class="divider"></div>` : ''}

        <!-- Battery -->
        ${hasBattery ? `
        <div class="section">
          <div class="section-title">Battery</div>
          <div id="battery-section"></div>
        </div>
        <div class="divider"></div>` : ''}

        <!-- Doors -->
        ${hasDoors ? `
        <div class="section">
          <div class="section-title">Doors &amp; Access</div>
          <div id="door-row" class="door-row door-row-3"></div>
        </div>
        <div class="divider"></div>` : ''}

        <!-- Lock -->
        ${hasLock ? `
        <div class="section">
          <div class="section-title">Lock</div>
          <div class="lock-row">
            <button class="lock-btn btn-lock" id="btn-lock"><ha-icon icon="mdi:lock"></ha-icon>Lock</button>
            <button class="lock-btn btn-unlock" id="btn-unlock"><ha-icon icon="mdi:lock-open"></ha-icon>Unlock</button>
          </div>
        </div>
        <div class="divider"></div>` : ''}

        <!-- Controls -->
        ${hasCtrl ? `
        <div class="section">
          <div class="section-title">Remote Controls</div>
          <div class="ctrl-grid ctrl-grid-3" id="ctrl-grid"></div>
        </div>
        <div class="divider"></div>` : ''}

        <!-- Settings -->
        ${hasSettings ? `
        <div class="section">
          <div class="section-title">Controller Settings</div>
          <div class="switch-list" id="switch-list"></div>
        </div>
        <div class="divider"></div>` : ''}

        <!-- Diagnostics -->
        ${hasDiag ? `
        <div class="section">
          <div class="section-title">Diagnostics</div>
          <div class="diag-list" id="diag-list"></div>
        </div>` : ''}

      </ha-card>
    `;

    this._buildStaticSections();
    this._bindButtons();
  }

  _buildStaticSections() {
    const r = this.shadowRoot;
    const on = (s, i) => this._on(s, i);

    // Status chips
    const chipGrid = r.getElementById('chip-grid');
    if (chipGrid) {
      const chips = [
        { key: 'engine',   icon: 'mdi:engine',      label: 'Engine',       id: 'val-engine' },
        { key: 'alarm',    icon: 'mdi:shield-car',   label: 'Alarm',        id: 'val-alarm' },
        { key: 'ignition', icon: 'mdi:key-variant',  label: 'Ignition',     id: 'val-ignition' },
        { key: 'remote',   icon: 'mdi:car-key',      label: 'Remote Start', id: 'val-remote' },
        { key: 'panic',    icon: 'mdi:alarm-light',  label: 'Panic',        id: 'val-panic' },
        { key: 'towing',   icon: 'mdi:tow-truck',    label: 'Towing',       id: 'val-tow' },
      ].filter(c => on('status', c.key));

      // 1→1col, 2→2col, 3→3col, 4→2col(2×2), 5-6→3col
      const chipCols = chips.length <= 2 ? chips.length : chips.length === 3 ? 3 : chips.length <= 4 ? 2 : 3;
      chipGrid.className = `chip-grid chip-grid-${chipCols}`;
      chipGrid.innerHTML = chips.map(c => `
        <div class="status-chip">
          <ha-icon icon="${c.icon}"></ha-icon>
          <div class="chip-label">${c.label}</div>
          <div class="chip-value" id="${c.id}">—</div>
        </div>
      `).join('');
    }

    // Telemetry
    const teleRow = r.getElementById('tele-row');
    if (teleRow) {
      const items = [
        { key: 'speed',    label: 'Speed',    id: 'val-speed' },
        { key: 'odometer', label: 'Odometer', id: 'val-odometer' },
        { key: 'temp',     label: 'Temp',     id: 'val-temp' },
        { key: 'heading',  label: 'Heading',  id: 'val-heading' },
      ].filter(i => on('telemetry', i.key));

      teleRow.innerHTML = items.map(i => `
        <div class="tele-item">
          <div class="tele-value" id="${i.id}">—</div>
          <div class="tele-label">${i.label}</div>
        </div>
      `).join('');
    }

    // Battery
    const batSec = r.getElementById('battery-section');
    if (batSec) {
      let html = '';
      if (on('battery', 'main_battery'))   html += `
        <div class="battery-card">
          <div class="battery-header">
            <ha-icon icon="mdi:car-battery" id="icon-bat-main"></ha-icon>
            <div class="battery-meta">
              <div class="battery-lbl">Main Battery</div>
              <div class="battery-status" id="bat-main-status">—</div>
            </div>
            <div class="battery-voltage" id="val-battery">—</div>
          </div>
          <div class="bar-wrap"><div class="bar" id="bar-main" style="width:0%"></div></div>
        </div>`;
      if (on('battery', 'backup_battery')) html += `
        <div class="battery-card">
          <div class="battery-header">
            <ha-icon icon="mdi:battery-heart" id="icon-bat-backup" style="color:var(--info-color,#2196F3)"></ha-icon>
            <div class="battery-meta">
              <div class="battery-lbl">Backup Battery</div>
              <div class="battery-status" id="bat-backup-status">—</div>
            </div>
            <div class="battery-voltage" id="val-backup">—</div>
          </div>
          <div class="bar-wrap"><div class="bar" id="bar-backup" style="width:0%;background:var(--info-color,#2196F3)"></div></div>
        </div>`;
      batSec.innerHTML = html;
    }

    // Doors
    const doorRow = r.getElementById('door-row');
    if (doorRow) {
      const doors = [
        { key: 'door',  icon: 'mdi:car-door', label: 'Door' },
        { key: 'trunk', icon: 'mdi:car-back',  label: 'Trunk' },
        { key: 'hood',  icon: 'mdi:car',       label: 'Hood' },
      ].filter(d => on('doors', d.key));

      doorRow.className = `door-row door-row-${doors.length <= 2 ? doors.length : 3}`;
      doorRow.innerHTML = doors.map(d => `
        <div class="door-chip">
          <ha-icon icon="${d.icon}" id="icon-${d.key}"></ha-icon>
          <div><div class="door-name">${d.label}</div><div class="door-state" id="val-${d.key}">—</div></div>
        </div>
      `).join('');
    }

    // Controls
    const ctrlGrid = r.getElementById('ctrl-grid');
    if (ctrlGrid) {
      const btns = [
        { key: 'remote_start', icon: 'mdi:play-circle',       label: 'Start',    color: 'var(--success-color)', id: 'btn-start' },
        { key: 'remote_stop',  icon: 'mdi:stop-circle',        label: 'Stop',     color: 'var(--error-color)',   id: 'btn-stop' },
        { key: 'trunk_btn',    icon: 'mdi:car-back',           label: 'Trunk',    color: 'var(--info-color,#2196F3)', id: 'btn-trunk' },
        { key: 'aux1',         icon: 'mdi:numeric-1-circle',   label: 'Aux 1',    color: '',                     id: 'btn-aux1' },
        { key: 'aux2',         icon: 'mdi:numeric-2-circle',   label: 'Aux 2',    color: '',                     id: 'btn-aux2' },
        { key: 'panic_btn',    icon: 'mdi:alarm-light',        label: 'Panic',    color: 'var(--warning-color)', id: 'btn-panic' },
      ].filter(b => on('controls', b.key));

      const ctrlCols = btns.length <= 2 ? btns.length : btns.length === 3 ? 3 : btns.length <= 4 ? 2 : 3;
      ctrlGrid.className = `ctrl-grid ctrl-grid-${ctrlCols}`;
      ctrlGrid.innerHTML = btns.map(b => `
        <button class="ctrl-btn" id="${b.id}">
          <ha-icon icon="${b.icon}" style="${b.color ? `color:${b.color}` : ''}"></ha-icon>
          <span>${b.label}</span>
        </button>
      `).join('');
    }

    // Settings switches
    const swList = r.getElementById('switch-list');
    if (swList && !swList._built) {
      swList._built = true;
      const switches = CARD_ITEMS.settings.items.filter(i => on('settings', i.key));
      swList.innerHTML = switches.map(s => `
        <div class="switch-row">
          <span class="switch-label">${s.label}</span>
          <ha-switch data-key="${s.key}"></ha-switch>
        </div>
      `).join('');

      swList.querySelectorAll('ha-switch').forEach(sw => {
        sw.addEventListener('change', e => {
          this._svc('switch', e.target.checked ? 'turn_on' : 'turn_off', this._eid('switch', e.target.dataset.key));
        });
      });
    }
  }

  _bindButtons() {
    const r = this.shadowRoot;
    // Call the custom service directly — bypasses HA's lock entity state guard
    // which silently no-ops when the entity is already locked/unlocked.
    r.getElementById('btn-lock')?.addEventListener('click',  () => this._hass.callService('drone_mobile_v2', 'send_lock',   {}));
    r.getElementById('btn-unlock')?.addEventListener('click',() => this._hass.callService('drone_mobile_v2', 'send_unlock', {}));
    r.getElementById('btn-start')?.addEventListener('click', () => this._btn('remote_start'));
    r.getElementById('btn-stop')?.addEventListener('click',  () => this._btn('remote_stop'));
    r.getElementById('btn-trunk')?.addEventListener('click', () => this._btn('trunk_release'));
    r.getElementById('btn-aux1')?.addEventListener('click',  () => this._btn('aux_1'));
    r.getElementById('btn-aux2')?.addEventListener('click',  () => this._btn('aux_2'));
    r.getElementById('btn-panic')?.addEventListener('click', () => this._btn('panic'));
  }

  // ── Battery helpers ────────────────────────────────────────────────────────

  _batteryPct(v) {
    // Non-linear mapping so 12.4 V looks like ~75% (healthy, not low)
    if (v >= 13.0) return 100;                                              // charging
    if (v >= 12.6) return 75 + ((v - 12.6) / 0.4) * 25;                   // 12.6→75% … 13.0→100%
    if (v >= 12.0) return 30 + ((v - 12.0) / 0.6) * 45;                   // 12.0→30% … 12.6→75%
    if (v >= 11.0) return Math.max(0, ((v - 11.0) / 1.0) * 30);           // 11.0→0%  … 12.0→30%
    return 0;
  }

  _batteryColor(v) {
    if (v >= 13.0) return 'var(--info-color, #2196F3)';    // charging
    if (v >= 12.4) return 'var(--success-color, #4CAF50)'; // good
    if (v >= 11.9) return 'var(--warning-color, #FF9800)'; // low
    return 'var(--error-color, #F44336)';                   // critical
  }

  _batteryStatus(v) {
    if (v >= 13.0) return 'Charging';
    if (v >= 12.4) return 'Good';
    if (v >= 11.9) return 'Low';
    if (v >= 11.2) return 'Critical';
    return 'Dead';
  }

  // ── Live update ────────────────────────────────────────────────────────────

  _update() {
    if (!this._hass || !this._config || !this._rendered) return;
    const r = this.shadowRoot;
    const on = (s, i) => this._on(s, i);

    // Last update
    const ts = this._state('sensor', 'last_known_state');
    if (ts && ts !== 'unavailable') {
      try {
        const d = new Date(ts);
        r.getElementById('last-update').textContent = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      } catch {}
    }

    // Mini map
    if (this._config.show_map !== false) this._updateMap();

    // Status
    if (on('status', 'engine'))   this._chip('engine',   this._state('sensor', 'engine_status'));
    if (on('status', 'alarm'))    this._chip('alarm',    this._state('sensor', 'alarm'));
    if (on('status', 'ignition')) this._chip('ignition', this._state('binary_sensor', 'ignition') === 'on' ? 'On' : 'Off');
    if (on('status', 'remote'))   this._chip('remote',   this._state('sensor', 'remote_start_status'));
    if (on('status', 'panic'))    this._chip('panic',    this._state('binary_sensor', 'panic_status') === 'on' ? 'Active' : 'Safe');
    if (on('status', 'towing'))   this._chip('tow',      this._state('binary_sensor', 'towing_detected') === 'on' ? 'Detected' : 'Clear');

    // Telemetry
    if (on('telemetry', 'speed')) {
      const v = this._state('sensor', 'speed'), u = this._attr('sensor', 'speed', 'unit_of_measurement') || '';
      this._text('val-speed', v !== 'unavailable' ? `${v} ${u}` : '—');
    }
    if (on('telemetry', 'odometer')) {
      const v = this._state('sensor', 'odometer'), u = this._attr('sensor', 'odometer', 'unit_of_measurement') || '';
      this._text('val-odometer', v !== 'unavailable' ? `${parseFloat(v).toLocaleString()} ${u}` : '—');
    }
    if (on('telemetry', 'temp')) {
      const v = this._state('sensor', 'vehicle_temperature'), u = this._attr('sensor', 'vehicle_temperature', 'unit_of_measurement') || '';
      this._text('val-temp', v !== 'unavailable' ? `${v}${u}` : '—');
    }
    if (on('telemetry', 'heading')) {
      const v = this._state('sensor', 'gps_direction');
      this._text('val-heading', v !== 'unavailable' ? v : '—');
    }

    // Battery
    if (on('battery', 'main_battery')) {
      const v = parseFloat(this._state('sensor', 'battery_voltage'));
      if (!isNaN(v)) {
        const color  = this._batteryColor(v);
        const status = this._batteryStatus(v);
        const pct    = this._batteryPct(v);
        this._text('val-battery', `${v.toFixed(1)} V`);
        this._text('bat-main-status', status);
        const icon = r.getElementById('icon-bat-main');
        if (icon) icon.style.color = color;
        const statusEl = r.getElementById('bat-main-status');
        if (statusEl) statusEl.style.color = color;
        const bar = r.getElementById('bar-main');
        if (bar) { bar.style.width = `${pct}%`; bar.style.background = color; }
      }
    }
    if (on('battery', 'backup_battery')) {
      const v = parseFloat(this._state('sensor', 'backup_battery_voltage'));
      if (!isNaN(v)) {
        this._text('val-backup', `${v.toFixed(2)} V`);
        const pct = Math.min(100, Math.max(0, ((v - 3.0) / 1.2) * 100));
        const statusEl = r.getElementById('bat-backup-status');
        if (statusEl) statusEl.textContent = v >= 3.7 ? 'Good' : v >= 3.4 ? 'Low' : 'Critical';
        const bar = r.getElementById('bar-backup');
        if (bar) bar.style.width = `${pct}%`;
      }
    }

    // Doors
    if (on('doors', 'door'))  this._door('door',  this._state('binary_sensor', 'door_status'));
    if (on('doors', 'trunk')) this._door('trunk', this._state('binary_sensor', 'trunk_status'));
    if (on('doors', 'hood'))  this._door('hood',  this._state('binary_sensor', 'hood_status'));

    // Settings
    r.getElementById('switch-list')?.querySelectorAll('ha-switch').forEach(sw => {
      sw.checked = this._state('switch', sw.dataset.key) === 'on';
    });

    // Diagnostics
    if (CARD_ITEMS.diagnostics.items.some(i => on('diagnostics', i.key))) {
      this._updateDiag();
    }
  }

  _updateMap() {
    const r = this.shadowRoot;
    const wrap = r.getElementById('map-wrap');
    if (!wrap) return;

    const tracker = this._e('device_tracker', 'location');
    if (!tracker) return;
    const lat = tracker.attributes?.latitude;
    const lon = tracker.attributes?.longitude;
    if (!lat || !lon) return;

    if (!wrap._mapBuilt) {
      wrap._mapBuilt = true;
      wrap.innerHTML = '';
      const haMap = document.createElement('ha-map');
      haMap.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;';
      haMap.zoom = this._config.map_zoom ?? 14;
      wrap.appendChild(haMap);
      wrap._haMap = haMap;
      // Async: wait for Leaflet inside ha-map to initialise, then add custom marker
      this._setupMapMarker(wrap);
    }

    wrap._haMap.hass = this._hass;
    // Pass entity so ha-map knows where to centre; we'll suppress its visual marker below
    wrap._haMap.entities = [{ entity_id: this._eid('device_tracker', 'location') }];

    // Move our custom Leaflet marker to latest GPS position
    if (wrap._customMarker) {
      wrap._customMarker.setLatLng([lat, lon]);
    }
  }

  // Returns the Leaflet namespace, loading from CDN if HA didn't expose window.L
  _getLeaflet() {
    if (this._leafletP) return this._leafletP;
    this._leafletP = new Promise(resolve => {
      if (window.L) { resolve(window.L); return; }
      const s = document.createElement('script');
      s.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
      s.onload = () => resolve(window.L);
      s.onerror  = () => resolve(null);
      document.head.appendChild(s);
    });
    return this._leafletP;
  }

  async _setupMapMarker(wrap) {
    // Poll until ha-map exposes its internal Leaflet map (up to ~10 s)
    let lMap;
    for (let i = 0; i < 40; i++) {
      await new Promise(res => setTimeout(res, 250));
      lMap = wrap._haMap?.leafletMap ?? wrap._haMap?._leafletMap;
      if (lMap) break;
    }
    if (!lMap) return;

    // Get Leaflet — try window.L first, fall back to CDN
    const L = await this._getLeaflet();
    if (!L) return;

    // Suppress ha-map's default "FL" entity badge via its Shadow DOM
    const shadow = wrap._haMap?.shadowRoot;
    if (shadow && !shadow.querySelector('#dm-v-style')) {
      const s = document.createElement('style');
      s.id = 'dm-v-style';
      s.textContent = 'ha-entity-marker { display:none!important; }';
      shadow.appendChild(s);
    }

    // Get current GPS position
    const tracker = this._e('device_tracker', 'location');
    const lat = tracker?.attributes?.latitude;
    const lon = tracker?.attributes?.longitude;
    if (!lat || !lon) return;

    const vehicleIcon = this._config.vehicle_icon || 'mdi:car-connected';
    const divIcon = L.divIcon({
      html: `<div style="width:36px;height:36px;border-radius:50%;
               background:var(--primary-color,#03a9f4);
               display:flex;align-items:center;justify-content:center;
               border:2.5px solid #fff;box-shadow:0 2px 10px rgba(0,0,0,0.45);
               box-sizing:border-box">
               <ha-icon icon="${vehicleIcon}"
                 style="--mdc-icon-size:18px;color:#fff;display:block">
               </ha-icon></div>`,
      iconSize:   [36, 36],
      iconAnchor: [18, 18],
      className:  '',
    });

    wrap._customMarker = L.marker([lat, lon], {
      icon: divIcon,
      interactive: false,
      zIndexOffset: 1000,
    }).addTo(lMap);
  }

  _updateDiag() {
    const r = this.shadowRoot;
    const list = r.getElementById('diag-list');
    if (!list) return;
    const on = (i) => this._on('diagnostics', i);

    const items = [
      { key: 'maintenance', label: 'Maintenance Due',  value: this._state('sensor', 'maintenance_due') },
      { key: 'low_battery', label: 'Low Battery',      value: this._state('binary_sensor', 'low_battery') === 'on' ? 'Yes' : 'No' },
      { key: 'firmware',    label: 'Firmware',          value: this._state('sensor', 'firmware_version') },
      { key: 'model',       label: 'Controller',        value: this._state('sensor', 'controller_model') },
      { key: 'carrier',     label: 'Carrier',           value: this._state('sensor', 'carrier') },
      { key: 'signal',      label: 'Signal',            value: this._state('sensor', 'cellular_signal') !== 'unavailable' ? `${this._state('sensor', 'cellular_signal')}%` : '—' },
      { key: 'last_cmd',    label: 'Last Command',      value: this._state('sensor', 'last_command') },
      { key: 'api_errors',  label: 'API Errors',        value: this._state('sensor', 'api_error_count') },
    ].filter(i => on(i.key));

    list.innerHTML = items.map(i => `
      <div class="diag-row">
        <span class="diag-key">${i.label}</span>
        <span class="diag-value">${i.value !== 'unavailable' ? i.value : '—'}</span>
      </div>
    `).join('');
  }

  _chip(id, state) {
    const el = this.shadowRoot.getElementById(`val-${id}`);
    if (!el) return;
    el.textContent = state || '—';
    const color = { running: 'var(--success-color)', armed: 'var(--success-color)', disarmed: 'var(--warning-color)', on: 'var(--success-color)', off: 'var(--secondary-text-color)', active: 'var(--error-color)', detected: 'var(--error-color)', clear: 'var(--success-color)', safe: 'var(--success-color)' };
    el.style.color = color[(state || '').toLowerCase()] || 'var(--primary-text-color)';
  }

  _door(id, haState) {
    const label = haState === 'on' ? 'Open' : haState === 'off' ? 'Closed' : '—';
    const color = haState === 'on' ? 'var(--error-color)' : 'var(--success-color)';
    const el   = this.shadowRoot.getElementById(`val-${id}`);
    const icon = this.shadowRoot.getElementById(`icon-${id}`);
    if (el)   { el.textContent = label; el.style.color = color; }
    if (icon) icon.style.color = color;
  }

  _text(id, val) {
    const el = this.shadowRoot.getElementById(id);
    if (el) el.textContent = val;
  }

  getCardSize() { return 8; }
}

customElements.define('drone-mobile-v2-card', DroneMobileV2Card);

window.customCards = window.customCards || [];
window.customCards.push({
  type: 'drone-mobile-v2-card',
  name: 'DroneMobile V2',
  description: 'Vehicle status card for the DroneMobile V2 integration.',
  preview: false,
  documentationURL: 'https://github.com/twoleftankles/HA-DroneMobileV2',
});

console.info(
  `%c DRONE-MOBILE-V2-CARD %c v${CARD_VERSION} `,
  'background:#1976D2;color:#fff;padding:2px 6px;border-radius:3px 0 0 3px;font-weight:bold;',
  'background:#424242;color:#fff;padding:2px 6px;border-radius:0 3px 3px 0;'
);
