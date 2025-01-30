import { ComponentFixture, TestBed } from '@angular/core/testing';

import { HelpGuideQuestionariesComponent } from './help-guide-questionaries.component';

describe('HelpGuideQuestionariesComponent', () => {
  let component: HelpGuideQuestionariesComponent;
  let fixture: ComponentFixture<HelpGuideQuestionariesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HelpGuideQuestionariesComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(HelpGuideQuestionariesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
