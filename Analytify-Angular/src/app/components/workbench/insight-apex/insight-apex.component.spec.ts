import { ComponentFixture, TestBed } from '@angular/core/testing';

import { InsightApexComponent } from './insight-apex.component';

describe('InsightApexComponent', () => {
  let component: InsightApexComponent;
  let fixture: ComponentFixture<InsightApexComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [InsightApexComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(InsightApexComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
