import { Component, OnInit, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FullCalendarModule } from '@fullcalendar/angular';
import { CalendarOptions, EventInput, EventApi, DateSelectArg, EventClickArg } from '@fullcalendar/core';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import ptBrLocale from '@fullcalendar/core/locales/pt-br';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { CalendarioService } from '../../services/calendario.service';
import { CalendarioEvento, CalendarioEventoCreate } from '../../interfaces/calendario.interface';
import { EventoDialogComponent } from './evento-dialog/evento-dialog.component';

@Component({
  selector: 'app-calendario',
  standalone: true,
  imports: [
    CommonModule,
    FullCalendarModule,
    MatButtonModule,
    MatIconModule,
    MatDialogModule,
    MatSnackBarModule
  ],
  templateUrl: './calendario.html',
  styleUrl: './calendario.scss',
})
export class CalendarioComponent implements OnInit, AfterViewInit {
  calendarOptions: CalendarOptions = {
    initialView: 'dayGridMonth',
    plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin],
    headerToolbar: {
      left: 'prev,next today',
      center: 'title',
      right: 'dayGridMonth,timeGridWeek,timeGridDay'
    },
    locale: ptBrLocale,
    firstDay: 1, // Segunda-feira
    selectable: true,
    selectMirror: true,
    dayMaxEvents: true,
    weekends: true,
    editable: true,
    droppable: false,
    select: this.handleDateSelect.bind(this),
    eventClick: this.handleEventClick.bind(this),
    eventsSet: this.handleEvents.bind(this),
    eventChange: this.handleEventChange.bind(this),
  };

  currentEvents: EventApi[] = [];
  calendarApi: any;

  constructor(
    private calendarioService: CalendarioService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadEvents();
  }

  ngAfterViewInit(): void {
    // Atualiza o tamanho do calendário após a view ser inicializada
    setTimeout(() => {
      if (this.calendarApi) {
        this.calendarApi.updateSize();
      }
    }, 300);
  }

  /**
   * Carrega eventos do backend
   */
  loadEvents(): void {
    this.calendarioService.list().subscribe({
      next: (eventos) => {
        const events: EventInput[] = eventos.map(evento => ({
          id: evento.id.toString(),
          title: evento.nome,
          start: evento.data,
          end: evento.data,
          backgroundColor: evento.cor || '#3788d8',
          borderColor: evento.cor || '#3788d8',
          extendedProps: {
            descricao: evento.descricao,
            cor: evento.cor
          }
        }));
        
        this.calendarOptions.events = events;
      },
      error: (error) => {
        console.error('Erro ao carregar eventos:', error);
        this.snackBar.open('Erro ao carregar eventos do calendário', 'Fechar', {
          duration: 3000
        });
      }
    });
  }

  /**
   * Manipula seleção de data (criar novo evento)
   */
  handleDateSelect(selectInfo: DateSelectArg): void {
    const dialogRef = this.dialog.open(EventoDialogComponent, {
      width: '500px',
      data: {
        data: selectInfo.startStr.split('T')[0], // YYYY-MM-DD
        evento: null
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.createEvent(result);
      }
      this.calendarApi.unselect();
    });
  }

  /**
   * Manipula clique em evento existente
   */
  handleEventClick(clickInfo: EventClickArg): void {
    const eventoId = parseInt(clickInfo.event.id);
    
    this.calendarioService.get(eventoId).subscribe({
      next: (evento) => {
        const dialogRef = this.dialog.open(EventoDialogComponent, {
          width: '500px',
          data: {
            data: evento.data,
            evento: evento
          }
        });

        dialogRef.afterClosed().subscribe(result => {
          if (result && result.action === 'delete') {
            this.deleteEvent(eventoId);
          } else if (result && result.action === 'update') {
            this.updateEvent(eventoId, result);
          }
        });
      },
      error: (error) => {
        console.error('Erro ao carregar evento:', error);
        this.snackBar.open('Erro ao carregar evento', 'Fechar', {
          duration: 3000
        });
      }
    });
  }

  /**
   * Manipula mudanças nos eventos (arrastar, redimensionar)
   */
  handleEventChange(changeInfo: any): void {
    const eventoId = parseInt(changeInfo.event.id);
    const startDate = changeInfo.event.startStr.split('T')[0];
    
    this.updateEvent(eventoId, { data: startDate });
  }

  /**
   * Atualiza lista de eventos quando o calendário é renderizado
   */
  handleEvents(events: EventApi[]): void {
    this.currentEvents = events;
  }

  /**
   * Cria novo evento
   */
  createEvent(eventoData: CalendarioEventoCreate): void {
    this.calendarioService.create(eventoData).subscribe({
      next: (evento) => {
        this.snackBar.open('Evento criado com sucesso!', 'Fechar', {
          duration: 3000
        });
        this.loadEvents();
      },
      error: (error) => {
        console.error('Erro ao criar evento:', error);
        this.snackBar.open('Erro ao criar evento', 'Fechar', {
          duration: 3000
        });
      }
    });
  }

  /**
   * Atualiza evento existente
   */
  updateEvent(id: number, eventoData: Partial<CalendarioEventoCreate>): void {
    this.calendarioService.update(id, eventoData).subscribe({
      next: (evento) => {
        this.snackBar.open('Evento atualizado com sucesso!', 'Fechar', {
          duration: 3000
        });
        this.loadEvents();
      },
      error: (error) => {
        console.error('Erro ao atualizar evento:', error);
        this.snackBar.open('Erro ao atualizar evento', 'Fechar', {
          duration: 3000
        });
        this.loadEvents(); // Recarrega para reverter mudanças visuais
      }
    });
  }

  /**
   * Remove evento
   */
  deleteEvent(id: number): void {
    this.calendarioService.delete(id).subscribe({
      next: () => {
        this.snackBar.open('Evento removido com sucesso!', 'Fechar', {
          duration: 3000
        });
        this.loadEvents();
      },
      error: (error) => {
        console.error('Erro ao remover evento:', error);
        this.snackBar.open('Erro ao remover evento', 'Fechar', {
          duration: 3000
        });
      }
    });
  }

  /**
   * Obtém referência da API do calendário
   */
  onCalendarReady(calendarApi: any): void {
    this.calendarApi = calendarApi;
    // Força o calendário a recalcular a altura após ser renderizado
    setTimeout(() => {
      if (calendarApi) {
        calendarApi.updateSize();
      }
    }, 100);
  }
}
