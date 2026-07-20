// @ts-nocheck
import { Scene } from 'phaser';

export class AdminMobileScene extends Scene {
  private cloutText!: Phaser.GameObjects.BitmapText;
  private coinsText!: Phaser.GameObjects.BitmapText;
  private currentTab: string = 'dashboard';
  private tabs: Phaser.GameObjects.Container[] = [];

  constructor() {
    super({ key: 'AdminMobileScene' });
  }

  create(): void {
    const { width, height } = this.scale;
    
    this.add.rectangle(0, 0, width, height, 0x0a0a12).setOrigin(0);
    
    this.createTopBar();
    this.createTabs();
    this.createDashboardContent();
    this.createUsersContent();
    this.createMarketContent();
    this.createLogsContent();
    this.createCommandsContent();
    
    this.setupMobileUI();
    this.loadAdminData();
    this.scale.on('resize', this.handleResize, this);
  }

  private createTopBar(): void {
    const { width } = this.scale;
    
    const topBar = this.add.graphics();
    topBar.fillStyle(0x0a0a12, 1);
    topBar.fillRect(0, 0, width, 70);
    topBar.lineStyle(2, 0xffd700, 1);
    topBar.lineBetween(0, 70, width, 70);
    
    this.add.bitmapText(15, 15, 'press-start', 'ADMIN PANEL', 24).setTint(0xffd700);
    this.add.bitmapText(15, 42, 'press-start-small', "LILITH'S LEDGER — ABYSSAL EXCHANGE", 10).setTint(0x88ffff);
    
    this.cloutText = this.add.bitmapText(width - 10, 15, 'press-start', 'RESONANCE: 0', 14).setOrigin(1, 0).setTint(0x00ff88);
    this.coinsText = this.add.bitmapText(width - 10, 38, 'press-start', 'SOUL COINS: 0', 14).setOrigin(1, 0).setTint(0xffd700);
    
    const backBtn = this.add.container(50, 35);
    const backBg = this.add.graphics();
    backBg.fillStyle(0x1a1a2e, 1);
    backBg.fillCircle(0, 0, 25);
    backBg.lineStyle(2, 0xff0000, 1);
    backBg.strokeCircle(0, 0, 25);
    const backIcon = this.add.bitmapText(0, 0, 'press-start', '←', 20).setOrigin(0.5).setTint(0xff0000);
    backBtn.add([backBg, backIcon]);
    backBtn.setSize(50, 50);
    backBtn.setInteractive();
    backBtn.on('pointerdown', () => {
      this.scene.stop();
      this.scene.resume('GameScene');
    });
  }

  private createTabs(): void {
    const { width } = this.scale;
    const tabs = [
      { id: 'dashboard', label: 'DASHBOARD', color: 0xffd700 },
      { id: 'users', label: 'USERS', color: 0x00ff88 },
      { id: 'market', label: 'MARKET', color: 0x00ffff },
      { id: 'logs', label: 'LOGS', color: 0xff8c00 },
      { id: 'commands', label: 'COMMANDS', color: 0xff00ff },
    ];
    
    tabs.forEach((tab, i) => {
      const x = 20 + i * 72;
      const container = this.add.container(x, 80);
      
      const bg = this.add.graphics();
      bg.fillStyle(this.currentTab === tab.id ? tab.color : 0x1a1a2e, 1);
      bg.fillRoundedRect(-30, -20, 64, 40, 6);
      bg.lineStyle(2, this.currentTab === tab.id ? tab.color : 0x333, 1);
      bg.strokeRoundedRect(-30, -20, 64, 40, 6);
      
      const text = this.add.bitmapText(0, 0, 'press-start-small', tab.label, 8).setOrigin(0.5).setTint(0xffffff);
      
      container.add([bg, text]);
      container.setSize(64, 40);
      container.setInteractive(new Phaser.Geom.Rectangle(-32, -20, 64, 40), Phaser.Geom.Rectangle.Contains);
      
      container.on('pointerover', () => {
        if (this.currentTab !== tab.id) {
          bg.clear().fillStyle(0x2a2a3e, 1).fillRoundedRect(-30, -20, 64, 40, 6)
            .lineStyle(2, tab.color, 1).strokeRoundedRect(-30, -20, 64, 40, 6);
        }
      });
      
      container.on('pointerout', () => {
        if (this.currentTab !== tab.id) {
          bg.clear().fillStyle(0x1a1a2e, 1).fillRoundedRect(-30, -20, 64, 40, 6)
            .lineStyle(2, 0x333, 1).strokeRoundedRect(-30, -20, 64, 40, 6);
        }
      });
      
      container.on('pointerdown', () => this.switchTab(tab.id));
      
      this.tabs.push(container);
    });
  }

  private switchTab(tabId: string): void {
    this.currentTab = tabId;
  }

  private createDashboardContent(): void {
    const stats = [
      { label: 'TOTAL USERS', value: 0, color: 0x00ffff },
      { label: 'ACTIVE TODAY', value: 0, color: 0x00ff88 },
      { label: 'TOTAL HATS', value: 0, color: 0xffd700 },
      { label: 'MARKET VOLUME', value: 0, color: 0xff8c00 },
      { label: 'AVG SESSION', value: '0m', color: 0x00ff88 },
      { label: 'REVENUE/DAU', value: '$0.00', color: 0xff00ff },
    ];
    
    stats.forEach((stat, i) => {
      const col = i % 3;
      const x = 10 + col * ((this.scale.width - 20) / 3);
      const y = 130 + Math.floor(i / 3) * 80;
      
      const container = this.add.container(x, y);
      
      const bg = this.add.graphics();
      bg.fillStyle(0x1a1a2e, 1);
      bg.fillRoundedRect(-((this.scale.width - 20) / 3) / 2 + 5, -30, (this.scale.width - 20) / 3 - 10, 60, 8);
      bg.lineStyle(1, 0x333, 1);
      bg.strokeRoundedRect(-((this.scale.width - 20) / 3) / 2 + 5, -30, (this.scale.width - 20) / 3 - 10, 60, 8);
      
      const label = this.add.bitmapText(0, -25, 'press-start-small', stat.label, 10).setOrigin(0.5).setTint(stat.color);
      const value = this.add.bitmapText(0, 5, 'press-start', stat.value.toString(), 18).setOrigin(0.5).setTint(0xffffff);
      
      container.add([bg, label, value]);
    });
  }

  private createUsersContent(): void {
    const { width } = this.scale;
    
    const searchBg = this.add.graphics();
    searchBg.fillStyle(0x1a1a2e, 1);
    searchBg.fillRoundedRect(10, 130, width - 20, 40, 8);
    searchBg.lineStyle(1, 0x333, 1);
    searchBg.strokeRoundedRect(10, 130, width - 20, 40, 8);
    
    this.add.bitmapText(20, 135, 'press-start-small', 'SEARCH USERS...', 14).setTint(0x888888);
    
    const usersList = [
      { name: 'Player1', clout: 1250, zone: 'Trench', status: 'ONLINE' },
      { name: 'Player2', clout: 890, zone: 'Abyssal', status: 'OFFLINE' },
      { name: 'Player3', clout: 2100, zone: 'Trench', status: 'ONLINE' },
      { name: 'Player4', clout: 540, zone: 'Deep', status: 'BUSY' },
      { name: 'Player5', clout: 3200, zone: 'Trench', status: 'ONLINE' },
    ];
    
    usersList.forEach((user, i) => {
      const y = 190 + i * 50;
      this.add.container(10, y);
      const bg = this.add.graphics();
      bg.fillStyle(0x1a1a2e, 1);
      bg.fillRoundedRect(0, 0, this.scale.width - 20, 45, 8);
      this.add.bitmapText(15, 5, 'press-start-small', user.name, 14).setTint(0xffd700);
      this.add.bitmapText(15, 22, 'press-start-small', `Clout: ${user.clout} | ${user.zone}`, 10).setTint(0x00ff88);
      this.add.bitmapText(this.scale.width - 100, 5, 'press-start-small', user.status, 12)
        .setTint(user.status === 'ONLINE' ? 0x00ff88 : 0x888888).setOrigin(1, 0);
    });
  }

  private createMarketContent(): void {
    this.add.bitmapText(20, 140, 'press-start', 'MARKET OVERVIEW', 18).setTint(0x00ffff);
    this.add.bitmapText(20, 180, 'press-start-small', 'Market data loads from Abyssal Exchange...', 12).setTint(0x888888);
  }

  private createLogsContent(): void {
    const { width, height } = this.scale;
    
    const logTabs = ['ALL', 'ERROR', 'WARN', 'DREDGE', 'TRADE', 'ADMIN', 'AUTH'];
    logTabs.forEach((tab, i) => {
      const x = i * 90 - 270;
      const btn = this.add.container(width / 2 + x, 140);
      const bg = this.add.graphics();
      bg.fillStyle(0x1a1a2e, 1);
      bg.fillRoundedRect(-40, -15, 80, 30, 6);
      bg.lineStyle(1, 0x333, 1);
      bg.strokeRoundedRect(-40, -15, 80, 30, 6);
      const text = this.add.bitmapText(0, 0, 'press-start-small', tab, 10).setOrigin(0.5).setTint(0x888888);
      btn.add([bg, text]);
    });
    
    const logBg = this.add.graphics();
    logBg.fillStyle(0x0a0a12, 0.9);
    logBg.fillRoundedRect(10, 180, this.scale.width - 20, this.scale.height - 200, 8);
    logBg.lineStyle(1, 0x333, 1);
    logBg.strokeRoundedRect(10, 180, this.scale.width - 20, this.scale.height - 200, 8);
    
    const sampleLogs = [
      '[INFO] Market sync completed',
      '[WARN] Dredge timeout in Deep zone',
      '[ERROR] Market API timeout',
      '[INFO] User Player1 purchased hat-kelp-top-hat',
      '[INFO] Dredge successful: hat-sub-captain-cap',
      '[WARN] Market price volatility detected',
      '[INFO] User Player2 listed hat-coral-tiara',
      '[INFO] System sync completed',
    ];
    
    sampleLogs.forEach((log, i) => {
      this.add.bitmapText(20, 190 + i * 22, 'press-start-small', log, 10).setTint(0x88ffff);
    });
  }

  private createCommandsContent(): void {
    const { width, height } = this.scale;
    const contentY = 130;
    
    const inputBg = this.add.graphics();
    inputBg.fillStyle(0x1a1a2e, 1);
    inputBg.fillRoundedRect(10, contentY, width - 20, 50, 8);
    inputBg.lineStyle(1, 0x333, 1);
    inputBg.strokeRoundedRect(10, contentY, width - 20, 50, 8);
    
    this.add.bitmapText(20, contentY + 15, 'press-start-small', 'COMMAND: ', 12).setTint(0x00ff88);
    
    const inputDiv = document.createElement('div');
    inputDiv.style.cssText = 'position: absolute; left: 100px; top: ' + (contentY + 5) + 'px; width: 250px;';
    const input = document.createElement('input');
    input.type = 'text';
    input.placeholder = 'Enter command... (e.g., /give @user hat-id)';
    input.style.cssText = 'width: 250px; height: 30px; background: #1a1a2e; border: 1px solid #333; color: #fff; font-family: monospace; font-size: 13px; padding: 0 10px; outline: none;';
    input.id = 'admin-command-input';
    inputDiv.appendChild(input);
    document.body.appendChild(inputDiv);
    (this as any).commandInputEl = input;
    
    const sendBtn = this.add.container(this.scale.width - 60, contentY + 25);
    const sendBg = this.add.graphics();
    sendBg.fillStyle(0x00ff88, 1);
    sendBg.fillRoundedRect(-50, -20, 100, 40, 8);
    const sendText = this.add.bitmapText(0, 0, 'press-start-small', 'SEND', 12).setOrigin(0.5).setTint(0x0a0a12);
    sendBtn.add([sendBg, sendText]);
    sendBtn.setSize(100, 40);
    sendBtn.setInteractive();
    sendBtn.on('pointerdown', () => this.sendCommand());
    
    const outputBg = this.add.graphics();
    outputBg.fillStyle(0x0a0a12, 0.95);
    outputBg.fillRoundedRect(10, 190, this.scale.width - 20, this.scale.height - 260, 8);
    outputBg.lineStyle(1, 0x333, 1);
    outputBg.strokeRoundedRect(10, 190, this.scale.width - 20, this.scale.height - 260, 8);
    
    this.add.bitmapText(20, 200, 'press-start-small', 'OUTPUT:', 12).setTint(0x00ff88);
  }

  private switchTab(tabId: string): void {
    this.currentTab = tabId;
  }

  private showUserDetails(user: { name: string; clout: number; zone: string; status: string; xp?: number; coins?: number }): void {
    const { width, height } = this.scale;
    
    const overlay = this.add.container(width / 2, height / 2);
    
    const bg = this.add.graphics();
    bg.fillStyle(0x0a0a12, 0.95);
    bg.fillRoundedRect(-200, -150, 400, 300, 16);
    bg.lineStyle(2, 0xffd700, 1);
    bg.strokeRoundedRect(-200, -150, 400, 300, 16);
    
    const title = this.add.bitmapText(0, -120, 'press-start', 'USER DETAILS', 20).setOrigin(0.5).setTint(0xffd700);
    
    const info = [
      `Name: ${user.name}`,
      `Clout: ${user.clout}`,
      `Zone: ${user.zone}`,
      `Status: ${user.status}`,
      `XP: ${user.xp || 0}`,
      `Soul Coins: ${user.coins || 0}`,
    ];
    
    info.forEach((line, i) => {
      this.add.bitmapText(0, -80 + i * 30, 'press-start-small', line, 14).setOrigin(0.5).setTint(0xe8d5c4);
    });
    
    const closeBtn = this.add.container(0, 120);
    const closeBg = this.add.graphics();
    closeBg.fillStyle(0xffd700, 1);
    closeBg.fillRoundedRect(-80, -20, 160, 40, 8);
    closeBtn.add([closeBg, this.add.bitmapText(0, 0, 'press-start', 'CLOSE', 16).setOrigin(0.5).setTint(0x0a0a12)]);
    closeBtn.setSize(160, 40);
    closeBtn.setInteractive();
    closeBtn.on('pointerdown', () => overlay.destroy());
    
    overlay.add([bg, title, closeBtn]);
  }

  private sendCommand(): void {
    const input = (this as any).commandInputEl;
    if (!input || !input.value.trim()) return;
    
    const cmd = input.value.trim();
    input.value = '';
    
    this.appendOutput(`> ${cmd}`);
    
    const queue = (window as any).adminQueue;
    if (queue) {
      queue.execute(cmd.split(' ')[0], ...cmd.split(' ').slice(1)).then(
        (result: any) => this.appendOutput(JSON.stringify(result, null, 2)),
        (error: any) => this.appendOutput(`Error: ${error.message}`)
      );
    } else {
      this.appendOutput('Queue not available');
    }
  }

  private appendOutput(text: string): void {
    console.log(text);
  }

  private setupMobileUI(): void {
    const meta = document.createElement('meta');
    meta.name = 'viewport';
    meta.content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover';
    document.head.appendChild(meta);
    
    const style = document.createElement('style');
    style.textContent = `
      .safe-area-top { padding-top: env(safe-area-inset-top); }
      .safe-area-bottom { padding-bottom: env(safe-area-inset-bottom); }
      .safe-area-left { padding-left: env(safe-area-inset-left); }
      .safe-area-right { padding-right: env(safe-area-inset-right); }
    `;
    document.head.appendChild(style);
  }

  private handleResize(_gameSize: Phaser.Structs.Size): void {
  }

  shutdown(): void {
    this.scale.off('resize', this.handleResize, this);
    const input = (this as any).commandInputEl;
    if (input && input.parentNode) {
      input.parentNode.removeChild(input);
    }
  }

  private loadAdminData(): void {
    fetch('/api/admin/dashboard')
      .then((res: Response) => res.json())
      .then((data: any) => {
        if (this.cloutText) this.cloutText.setText(`RESONANCE: ${data.clout || 0}`);
        if (this.coinsText) this.coinsText.setText(`SOUL COINS: ${data.coins || 0}`);
      })
      .catch(() => {});
    
    fetch('/api/admin/logs?limit=50')
      .then((res: Response) => res.json())
      .then(() => {})
      .catch(() => {});
  }
}