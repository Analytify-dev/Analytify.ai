import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SheetsdashboardComponent } from './sheetsdashboard.component';

describe('SheetsdashboardComponent', () => {
  let component: SheetsdashboardComponent;
  let fixture: ComponentFixture<SheetsdashboardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SheetsdashboardComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(SheetsdashboardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
