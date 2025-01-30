import { ComponentFixture, TestBed } from '@angular/core/testing';

import { InsightEchartComponent } from './insight-echart.component';

describe('InsightEchartComponent', () => {
  let component: InsightEchartComponent;
  let fixture: ComponentFixture<InsightEchartComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [InsightEchartComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(InsightEchartComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
