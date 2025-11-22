import { Injectable } from '@angular/core';
import { Observable, Subject } from 'rxjs';

export interface Brick {
  origin: number[];
  dims: number[];
  energyU8: number[];
}

export interface ViewconePacket {
  tick: number;
  camPos: number[];
  camDir: number[];
  brickSize: number;
  bricks: Brick[];
}

@Injectable({ providedIn: 'root' })
export class ViewconeService {
  private subject = new Subject<ViewconePacket>();

  connect(): Observable<ViewconePacket> {
    const socket = new WebSocket('ws://localhost:8080/viewcone');

    socket.onmessage = (event) => {
      try {
        const packet = JSON.parse(event.data);
        this.subject.next(packet);
      } catch (e) {
        console.error('Bad packet', e);
      }
    };

    return this.subject.asObservable();
  }
}
