import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChartsStoreComponent } from './charts-store.component';

describe('ChartsStoreComponent', () => {
  let component: ChartsStoreComponent;
  let fixture: ComponentFixture<ChartsStoreComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ChartsStoreComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(ChartsStoreComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
