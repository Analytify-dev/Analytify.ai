import { ComponentFixture, TestBed } from '@angular/core/testing';

import { QuickbooksComponent } from './quickbooks.component';

describe('QuickbooksComponent', () => {
  let component: QuickbooksComponent;
  let fixture: ComponentFixture<QuickbooksComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [QuickbooksComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(QuickbooksComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
