import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SheetsListPageComponent } from './sheets-list-page.component';

describe('SheetsListPageComponent', () => {
  let component: SheetsListPageComponent;
  let fixture: ComponentFixture<SheetsListPageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SheetsListPageComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(SheetsListPageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
